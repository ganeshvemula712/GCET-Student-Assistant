import asyncio
import gc
import logging
import threading
from io import BytesIO

from backend.app.core.database import SessionLocal
from backend.app.models.document import Document
from backend.app.services.embeddings import generate_embeddings, _cached_query_embedding
from backend.app.services.ocr import extract_document_pages, GeminiQuotaExhaustedError
from backend.app.services.storage import download_file_from_storage, get_storage_key
from backend.app.services.text_processing import chunk_text
from backend.app.services.vector_store import get_collection, store_chunks
from backend.app.services.documents import (
    acquire_reindex_lock,
    is_reindexing_in_progress,
    release_reindex_lock,
)
from google.genai import types

from sqlalchemy import or_
from backend.app.core.config import settings

logger = logging.getLogger("uvicorn")
_SELF_HEAL_CYCLE_LOCK = threading.Lock()


def _reindex_document_from_bytes(doc: Document, content: bytes) -> int:
    try:
        page_count, extracted_pages = extract_document_pages(content, doc.filename)
    except GeminiQuotaExhaustedError as quota_err:
        logger.error(f"[SELF-HEAL] Quota exhausted during document re-indexing for '{doc.filename}': {quota_err}")
        return 0
    except Exception as err:
        logger.error(f"[SELF-HEAL] Extraction failed for '{doc.filename}': {err}")
        return 0

    all_chunks = []
    for p_num, p_text in extracted_pages:
        page_chunks = chunk_text(
            text=p_text,
            filename=doc.filename,
            page_number=p_num,
            document_id=doc.document_id,
            chunk_size=1000,
            chunk_overlap=200,
            category=doc.category or "General",
            tags=doc.tags or "",
        )
        for chunk in page_chunks:
            chunk["metadata"]["version"] = doc.version or 1
            chunk["metadata"]["is_active"] = True
            chunk["metadata"]["category"] = doc.category or "General"
            chunk["metadata"]["tags"] = doc.tags or ""
            all_chunks.append(chunk)

    if not all_chunks:
        return 0

    try:
        texts = [chunk["text"] for chunk in all_chunks]
        embeddings = generate_embeddings(texts)
        store_chunks(chunks=all_chunks, embeddings=embeddings)
        return len(all_chunks)
    except Exception as err:
        logger.error(f"[SELF-HEAL] Vector storage failed for '{doc.filename}': {err}")
        return 0
    finally:
        del all_chunks
        gc.collect()


import json
from backend.app.services.storage import get_vector_storage_key


def _validate_vector_payload(payload: dict, expected_document_id: str) -> bool:
    """
    Validates vector payload JSON structure, count consistency, and non-empty embeddings.
    """
    if not isinstance(payload, dict):
        return False
    if payload.get("document_id") != expected_document_id:
        return False

    ids = payload.get("ids")
    documents = payload.get("documents")
    metadatas = payload.get("metadatas")
    embeddings = payload.get("embeddings")

    if not (isinstance(ids, list) and isinstance(documents, list) and isinstance(metadatas, list) and isinstance(embeddings, list)):
        return False

    n = len(ids)
    if n == 0 or len(documents) != n or len(metadatas) != n or len(embeddings) != n:
        return False

    first_emb = embeddings[0]
    if not isinstance(first_emb, list) or len(first_emb) == 0:
        return False

    return True


def sync_chromadb_with_postgres() -> None:
    """
    Self-healing background worker:
    Scans active and indexing_required PostgreSQL document records against ChromaDB vector storage.
    If vectors are missing (e.g. after ephemeral disk wipe), attempts to restore from vectors/{document_id}.json
    in Supabase Storage WITHOUT calling Gemini Embeddings API.
    If vector JSON is missing or invalid, falls back to source file re-indexing.
    Sequential, memory-safe execution with in-process lock protection.
    """
    if not _SELF_HEAL_CYCLE_LOCK.acquire(blocking=False):
        logger.warning("[SELF-HEAL] Previous self-healing cycle is still in progress. Skipping duplicate run.")
        return

    logger.info("[SELF-HEAL] Starting ChromaDB vector persistence check...")
    db = SessionLocal()
    try:
        target_docs = (
            db.query(Document)
            .filter(
                or_(
                    Document.is_active == True,
                    Document.status == "indexing_required",
                )
            )
            .all()
        )
        logger.info(f"[SELF-HEAL] Found {len(target_docs)} document records to verify in PostgreSQL.")

        coll = get_collection()

        for doc in target_docs:
            if is_reindexing_in_progress(doc.document_id):
                logger.info(f"[SELF-HEAL] Document '{doc.filename}' ({doc.document_id[:8]}) is already being re-indexed. Skipping...")
                continue

            if not acquire_reindex_lock(doc.document_id):
                continue

            try:
                res = coll.get(where={"document_id": doc.document_id})
                chunk_count = len(res.get("ids", []))

                if chunk_count > 0:
                    logger.info(f"[SELF-HEAL] Document '{doc.filename}' ({doc.document_id[:8]}) verified: {chunk_count} vectors in ChromaDB.")
                    if doc.status != "processed" or doc.is_active is False:
                        doc.status = "processed"
                        doc.is_active = True
                        doc.chunk_count = chunk_count
                else:
                    logger.warning(f"[SELF-HEAL] Vectors missing for document '{doc.filename}' ({doc.document_id[:8]}). Checking Supabase vector backup...")
                    vector_key = get_vector_storage_key(doc.document_id)
                    vector_bytes = download_file_from_storage(vector_key)

                    restored_from_json = False
                    if vector_bytes:
                        try:
                            payload = json.loads(vector_bytes.decode("utf-8"))
                            if _validate_vector_payload(payload, doc.document_id):
                                coll.upsert(
                                    ids=payload["ids"],
                                    documents=payload["documents"],
                                    metadatas=payload["metadatas"],
                                    embeddings=payload["embeddings"],
                                )
                                restored_count = len(payload["ids"])
                                doc.status = "processed"
                                doc.is_active = True
                                doc.chunk_count = restored_count
                                restored_from_json = True
                                logger.info(
                                    f"[SELF-HEAL RESTORE] Restored '{doc.filename}': {restored_count} vectors loaded directly from "
                                    f"Supabase Storage '{vector_key}' WITHOUT Gemini embedding API calls."
                                )
                                del payload
                            else:
                                logger.warning(f"[SELF-HEAL RESTORE] Vector payload '{vector_key}' for '{doc.filename}' failed validation. Falling back to re-indexing.")
                        except Exception as val_err:
                            logger.warning(f"[SELF-HEAL RESTORE] Error reading vector payload '{vector_key}' for '{doc.filename}': {val_err}")
                        finally:
                            del vector_bytes

                    if restored_from_json:
                        continue

                    # Fallback to source document re-indexing if vector payload backup is unavailable or invalid
                    logger.warning(f"[SELF-HEAL] Vector backup unavailable for '{doc.filename}'. Re-indexing from original source file...")
                    obj_key = get_storage_key(doc.document_id, doc.filename)
                    content = download_file_from_storage(obj_key)

                    if content:
                        new_count = _reindex_document_from_bytes(doc, content)
                        del content
                        if new_count > 0:
                            doc.status = "processed"
                            doc.is_active = True
                            doc.chunk_count = new_count
                            logger.info(f"[SELF-HEAL] Successfully restored '{doc.filename}': {new_count} chunks indexed into ChromaDB.")
                        else:
                            if doc.status == "processed" and doc.is_active is True and (doc.chunk_count or 0) > 0:
                                logger.warning(
                                    f"[SELF-HEAL] Re-indexing temporarily failed for previously processed '{doc.filename}'. "
                                    f"Preserving existing PostgreSQL state (chunk_count={doc.chunk_count})."
                                )
                            else:
                                doc.status = "indexing_required"
                                doc.is_active = False
                                doc.chunk_count = 0
                                logger.error(f"[SELF-HEAL] Re-indexing failed or empty for '{doc.filename}'. Status set to indexing_required.")
                    else:
                        if doc.status == "processed" and doc.is_active is True and (doc.chunk_count or 0) > 0:
                            logger.warning(
                                f"[SELF-HEAL] Source file for '{doc.filename}' temporarily unretrievable. "
                                f"Preserving existing PostgreSQL state (chunk_count={doc.chunk_count})."
                            )
                        else:
                            doc.status = "indexing_required"
                            doc.is_active = False
                            doc.chunk_count = 0
                            logger.warning(f"[SELF-HEAL] Source file for '{doc.filename}' not found in storage. Marked indexing_required.")
            except Exception as doc_err:
                logger.error(f"[SELF-HEAL] Error checking/healing document '{doc.filename}': {doc_err}")
            finally:
                release_reindex_lock(doc.document_id)
                gc.collect()

        db.commit()
        _cached_query_embedding.cache_clear()
        logger.info("[SELF-HEAL] Vector persistence check completed successfully.")
    except Exception as err:
        db.rollback()
        logger.error(f"[SELF-HEAL] Critical error during ChromaDB synchronization: {err}")
    finally:
        db.close()
        _SELF_HEAL_CYCLE_LOCK.release()
        gc.collect()


async def run_async_self_healing():
    """Run self-healing task in background with recurring schedule."""
    interval_seconds = getattr(settings, "SELF_HEALING_INTERVAL_MINUTES", 60) * 60
    logger.info(f"[SELF-HEAL] Background scheduler started (Interval: {interval_seconds // 60}m).")
    await asyncio.sleep(2)
    while True:
        try:
            logger.info("[SELF-HEAL CYCLE] Starting scheduled self-healing cycle...")
            await asyncio.to_thread(sync_chromadb_with_postgres)
            logger.info("[SELF-HEAL CYCLE] Scheduled self-healing cycle finished.")
        except Exception as cycle_err:
            logger.error(f"[SELF-HEAL CYCLE] Error in background cycle: {cycle_err}")
        await asyncio.sleep(interval_seconds)
