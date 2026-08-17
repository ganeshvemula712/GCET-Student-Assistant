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


def sync_chromadb_with_postgres() -> None:
    """
    Self-healing background worker:
    Scans active and indexing_required PostgreSQL document records against ChromaDB vector storage.
    If vectors are missing (e.g. after ephemeral disk wipe or rate limit reset), downloads source file
    from Supabase Storage and re-indexes into ChromaDB automatically.
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
                    logger.warning(f"[SELF-HEAL] Vectors missing for document '{doc.filename}' ({doc.document_id[:8]}). Healing from storage...")
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
                            doc.status = "indexing_required"
                            doc.is_active = False
                            doc.chunk_count = 0
                            logger.error(f"[SELF-HEAL] Re-indexing failed or empty for '{doc.filename}'. Status set to indexing_required.")
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
