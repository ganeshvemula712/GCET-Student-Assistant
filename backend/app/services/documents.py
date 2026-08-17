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
    get_storage_key,
    upload_file_to_storage,
)
from backend.app.services.vector_store import (
    delete_document_chunks,
    mark_document_chunks_inactive,
    store_chunks,
)
from google.genai import types


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
    category: str | None = None,
) -> list[Document]:
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

    # Dynamic status verification against ChromaDB
    try:
        coll = get_collection()
        for doc in docs:
            if doc.is_active:
                res = coll.get(where={"document_id": doc.document_id})
                vector_count = len(res.get("ids", []))
                if vector_count == 0 and doc.status == "processed":
                    doc.status = "indexing_required"
    except Exception:
        pass

    return docs


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