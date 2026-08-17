import gc
import threading
from hashlib import sha256
from io import BytesIO

from fastapi import HTTPException, UploadFile
from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.app.models.document import Document, DEFAULT_CATEGORY, VALID_CATEGORIES
from backend.app.services.embeddings import generate_embeddings, _cached_query_embedding
from backend.app.services.text_processing import chunk_text
from backend.app.services.ocr import extract_document_pages, GeminiQuotaExhaustedError
from backend.app.services.storage import (
    delete_file_from_storage,
    download_file_from_storage,
    get_storage_key,
    upload_file_to_storage,
)
from backend.app.services.vector_store import (
    delete_document_chunks,
    get_collection,
    mark_document_chunks_inactive,
    store_chunks,
)
from google.genai import types

_REINDEXING_IN_PROGRESS = set()
_REINDEX_LOCK = threading.Lock()


def is_reindexing_in_progress(document_id: str) -> bool:
    with _REINDEX_LOCK:
        return document_id in _REINDEXING_IN_PROGRESS


def acquire_reindex_lock(document_id: str) -> bool:
    with _REINDEX_LOCK:
        if document_id in _REINDEXING_IN_PROGRESS:
            return False
        _REINDEXING_IN_PROGRESS.add(document_id)
        return True


def release_reindex_lock(document_id: str) -> None:
    with _REINDEX_LOCK:
        _REINDEXING_IN_PROGRESS.discard(document_id)


def normalize_tags(tags_input: str | None) -> str:
    if not tags_input:
        return ""
    raw_tags = [t.strip() for t in tags_input.split(",")]
    seen = set()
    clean_tags = []
    for t in raw_tags:
        if t and t.lower() not in seen:
            seen.add(t.lower())
            clean_tags.append(t)
    return ", ".join(clean_tags)


async def process_document(
    file: UploadFile,
    db: Session,
    supersedes_id: str | None = None,
    category: str | None = None,
    tags: str | None = None,
) -> dict:
    filename_lower = file.filename.lower()
    allowed_extensions = (".pdf", ".docx", ".doc", ".jpg", ".jpeg", ".png")

    if not any(filename_lower.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Supported formats: PDF, DOCX, DOC, JPG, JPEG, PNG.",
        )

    # Category Validation & Tag Normalization
    category_clean = (category or "").strip()
    if category_clean and category_clean not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category '{category_clean}'. Supported categories: {', '.join(VALID_CATEGORIES)}",
        )
    final_category = category_clean if category_clean else DEFAULT_CATEGORY
    final_tags = normalize_tags(tags)

    # Read uploaded file
    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty",
        )

    # Generate unique document ID
    document_id = sha256(content).hexdigest()

    # Upload raw file bytes to permanent storage (Cloudflare R2 / local fallback)
    object_key = get_storage_key(document_id, file.filename)
    storage_ok = upload_file_to_storage(content, object_key)
    if not storage_ok:
        raise HTTPException(
            status_code=500,
            detail="Failed to persist raw file to cloud storage.",
        )

    # Check whether document already exists
    existing_document = (
        db.query(Document)
        .filter(Document.document_id == document_id)
        .first()
    )

    if existing_document:
        raise HTTPException(
            status_code=409,
            detail="This document has already been uploaded",
        )

    page_count = 1
    extracted_pages = []
    ocr_quota_exhausted = False

    try:
        page_count, extracted_pages = extract_document_pages(content, file.filename)
    except GeminiQuotaExhaustedError as quota_err:
        ocr_quota_exhausted = True
        logger.error(f"[UPLOAD] Quota exhausted during document extraction: {quota_err}")
    except Exception as parse_err:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse document: {str(parse_err)}",
        )

    # Handle Versioning
    new_version = 1
    if supersedes_id:
        old_doc = (
            db.query(Document)
            .filter(Document.document_id == supersedes_id)
            .first()
        )
        if old_doc:
            new_version = (old_doc.version or 1) + 1
            old_doc.is_active = False
            mark_document_chunks_inactive(old_doc.document_id)

    all_chunks = []
    for p_num, p_text in extracted_pages:
        page_chunks = chunk_text(
            text=p_text,
            filename=file.filename,
            page_number=p_num,
            document_id=document_id,
            chunk_size=1000,
            chunk_overlap=200,
            category=final_category,
            tags=final_tags,
        )
        for chunk in page_chunks:
            chunk["metadata"]["version"] = new_version
            chunk["metadata"]["is_active"] = True
            chunk["metadata"]["category"] = final_category
            chunk["metadata"]["tags"] = final_tags
            all_chunks.append(chunk)

    if ocr_quota_exhausted:
        new_document = Document(
            document_id=document_id,
            filename=file.filename,
            page_count=page_count,
            chunk_count=0,
            status="indexing_required",
            version=new_version,
            is_active=False,
            supersedes_id=supersedes_id,
            category=final_category,
            tags=final_tags,
        )
        db.add(new_document)
        db.commit()
        raise HTTPException(
            status_code=429,
            detail="Document uploaded successfully, but OCR indexing could not be completed because the Gemini OCR quota is currently exhausted. Please retry after the quota resets.",
        )

    if not all_chunks:
        raise HTTPException(
            status_code=400,
            detail="No readable text or content found in uploaded document",
        )

    # Generate Embeddings
    try:
        texts = [chunk["text"] for chunk in all_chunks]
        embeddings = generate_embeddings(texts)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Embedding generation failed",
        )

    # Store Chunks in ChromaDB
    try:
        store_chunks(
            chunks=all_chunks,
            embeddings=embeddings,
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to store vectors in ChromaDB",
        )

    # Save to PostgreSQL
    new_document = Document(
        document_id=document_id,
        filename=file.filename,
        page_count=page_count,
        chunk_count=len(all_chunks),
        status="processed",
        version=new_version,
        is_active=True,
        supersedes_id=supersedes_id,
        category=final_category,
        tags=final_tags,
    )

    try:
        db.add(new_document)
        db.commit()
        db.refresh(new_document)

    except Exception:
        db.rollback()
        delete_document_chunks(document_id)
        raise HTTPException(
            status_code=500,
            detail="Failed to save document record",
        )

    return {
        "id": new_document.id,
        "document_id": new_document.document_id,
        "filename": new_document.filename,
        "page_count": new_document.page_count,
        "chunk_count": new_document.chunk_count,
        "status": new_document.status,
        "version": new_document.version,
        "is_active": new_document.is_active,
        "supersedes_id": new_document.supersedes_id,
        "category": new_document.category or DEFAULT_CATEGORY,
        "tags": new_document.tags or "",
        "uploaded_at": new_document.uploaded_at,
        "message": f"Document '{file.filename}' (v{new_version}) categorized as '{final_category}' processed and indexed successfully into ChromaDB!",
    }


def get_documents(
    db: Session,
    category: str | None = Query(None) if False else None,
) -> list[dict]:
    query = db.query(Document)
    if category:
        cat_clean = category.strip()
        if cat_clean.lower() == DEFAULT_CATEGORY.lower():
            query = query.filter(
                or_(
                    Document.category.ilike(cat_clean),
                    Document.category.is_(None),
                )
            )
        else:
            query = query.filter(Document.category.ilike(cat_clean))
    docs = query.order_by(Document.uploaded_at.desc()).all()

    result_docs = []
    try:
        coll = get_collection()
        for doc in docs:
            doc_dict = {
                "id": doc.id,
                "document_id": doc.document_id,
                "filename": doc.filename,
                "page_count": doc.page_count,
                "chunk_count": doc.chunk_count,
                "status": doc.status,
                "version": doc.version,
                "is_active": doc.is_active,
                "supersedes_id": doc.supersedes_id,
                "category": doc.category or DEFAULT_CATEGORY,
                "tags": doc.tags or "",
                "uploaded_at": doc.uploaded_at,
            }
            try:
                res = coll.get(where={"document_id": doc.document_id})
                vector_count = len(res.get("ids", []))
                if vector_count == 0:
                    if doc_dict["is_active"] or doc_dict["status"] == "processed":
                        doc_dict["status"] = "indexing_required"
                        doc_dict["is_active"] = False
                    doc_dict["chunk_count"] = 0
                else:
                    doc_dict["chunk_count"] = vector_count
            except Exception:
                pass
            result_docs.append(doc_dict)
    except Exception:
        result_docs = [
            {
                "id": doc.id,
                "document_id": doc.document_id,
                "filename": doc.filename,
                "page_count": doc.page_count,
                "chunk_count": doc.chunk_count,
                "status": doc.status,
                "version": doc.version,
                "is_active": doc.is_active,
                "supersedes_id": doc.supersedes_id,
                "category": doc.category or DEFAULT_CATEGORY,
                "tags": doc.tags or "",
                "uploaded_at": doc.uploaded_at,
            }
            for doc in docs
        ]

    return result_docs


def remove_document(
    document_id: str,
    db: Session,
) -> dict:
    document = (
        db.query(Document)
        .filter(Document.document_id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    filename = document.filename
    object_key = get_storage_key(document_id, filename)

    delete_document_chunks(document_id)
    delete_file_from_storage(object_key)

    db.delete(document)
    db.commit()

    _cached_query_embedding.cache_clear()

    return {
        "message": "Document deleted successfully",
        "document_id": document_id,
        "filename": filename,
    }


def reindex_document(
    document_id: str,
    db: Session,
) -> dict:
    doc = (
        db.query(Document)
        .filter(Document.document_id == document_id)
        .first()
    )
    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    if not acquire_reindex_lock(document_id):
        raise HTTPException(
            status_code=409,
            detail=f"Document '{doc.filename}' is currently being indexed or self-healed. Please try again shortly.",
        )

    try:
        object_key = get_storage_key(doc.document_id, doc.filename)
        content = download_file_from_storage(object_key)
        if not content:
            doc.status = "indexing_required"
            doc.is_active = False
            db.commit()
            raise HTTPException(
                status_code=400,
                detail=f"Original source file for '{doc.filename}' not found in cloud storage",
            )

        try:
            page_count, extracted_pages = extract_document_pages(content, doc.filename)
        except GeminiQuotaExhaustedError as quota_err:
            doc.status = "indexing_required"
            doc.is_active = False
            doc.chunk_count = 0
            db.commit()
            raise HTTPException(
                status_code=429,
                detail="Document re-indexing could not be completed because the Gemini OCR quota is currently exhausted. Please retry after the quota resets.",
            )
        except Exception as parse_err:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse document: {str(parse_err)}",
            )
        finally:
            del content

        all_chunks = []
        for p_num, p_text in extracted_pages:
            page_chunks = chunk_text(
                text=p_text,
                filename=doc.filename,
                page_number=p_num,
                document_id=doc.document_id,
                chunk_size=1000,
                chunk_overlap=200,
                category=doc.category or DEFAULT_CATEGORY,
                tags=doc.tags or "",
            )
            for chunk in page_chunks:
                chunk["metadata"]["version"] = doc.version or 1
                chunk["metadata"]["is_active"] = True
                chunk["metadata"]["category"] = doc.category or DEFAULT_CATEGORY
                chunk["metadata"]["tags"] = doc.tags or ""
                all_chunks.append(chunk)

        if not all_chunks:
            doc.status = "indexing_required"
            doc.is_active = False
            doc.chunk_count = 0
            db.commit()
            raise HTTPException(
                status_code=400,
                detail="No readable text or content extracted from original document",
            )

        try:
            texts = [chunk["text"] for chunk in all_chunks]
            embeddings = generate_embeddings(texts)
        except Exception as emb_err:
            raise HTTPException(
                status_code=500,
                detail=f"Embedding generation failed: {str(emb_err)}",
            )

        try:
            store_chunks(chunks=all_chunks, embeddings=embeddings)
        except Exception as chroma_err:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to store vectors in ChromaDB: {str(chroma_err)}",
            )

        new_count = len(all_chunks)
        doc.status = "processed"
        doc.is_active = True
        doc.chunk_count = new_count
        db.commit()

        _cached_query_embedding.cache_clear()

        return {
            "message": f"Document '{doc.filename}' re-indexed successfully into ChromaDB!",
            "document_id": doc.document_id,
            "filename": doc.filename,
            "chunk_count": new_count,
            "status": "processed",
            "is_active": True,
        }
    finally:
        release_reindex_lock(document_id)
        gc.collect()