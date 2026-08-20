import chromadb


client = chromadb.PersistentClient(path="chroma_db")


def get_collection():
    return client.get_or_create_collection(name="gcet_documents")


collection = get_collection()


import json
import logging
from backend.app.services.storage import (
    delete_file_from_storage,
    get_vector_storage_key,
    upload_file_to_storage,
)


def validate_vector_payload(payload: dict, expected_document_id: str) -> bool:
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

logger = logging.getLogger("uvicorn")


def store_chunks(
    chunks: list[dict],
    embeddings: list[list[float]],
) -> None:

    if not chunks:
        return

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        metadata = dict(chunk["metadata"])
        if "is_active" not in metadata:
            metadata["is_active"] = True

        chunk_id = (
            f"{metadata['document_id']}_"
            f"{metadata['page']}_"
            f"{metadata['chunk_index']}"
        )

        ids.append(chunk_id)
        documents.append(chunk["text"])
        metadatas.append(metadata)

    coll = get_collection()
    coll.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    # Persist Vector Payload JSON to Supabase Storage
    try:
        doc_id = metadatas[0]["document_id"]
        vector_key = get_vector_storage_key(doc_id)
        json_embeddings = [[float(val) for val in vec] for vec in embeddings]
        payload = {
            "document_id": doc_id,
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas,
            "embeddings": json_embeddings,
        }
        payload_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        upload_success = upload_file_to_storage(
            content=payload_bytes,
            object_key=vector_key,
            content_type="application/json",
        )
        if upload_success:
            logger.info(f"[VECTOR STORE] Persisted vector payload '{vector_key}' ({len(payload_bytes)} bytes) to Supabase Storage.")
        else:
            logger.warning(f"[VECTOR STORE WARNING] Failed to persist vector payload '{vector_key}' to Supabase Storage.")
    except Exception as err:
        logger.error(f"[VECTOR STORE ERROR] Failed persisting vector payload for document: {err}")


SPELLING_NORM_MAP = {
    "calender": "calendar",
    "caleder": "calendar",
    "timetabl": "timetable",
    "time-table": "timetable",
}


def normalize_query_tokens_for_matching(query_text: str | None) -> str:
    """
    Normalize common spelling variations (e.g. 'calender' -> 'calendar')
    and year/sem abbreviations so metadata token matching works reliably against filename tokens.
    """
    if not query_text:
        return ""
    q_lower = query_text.lower().strip()
    for variant, canonical in SPELLING_NORM_MAP.items():
        q_lower = q_lower.replace(variant, canonical)
    return q_lower


def search_chunks(
    query_embedding: list[float],
    n_results: int = 3,
    query_text: str | None = None,
) -> list[dict]:

    coll = get_collection()
    # Priority 1: Query active document vectors only
    try:
        results = coll.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={"is_active": True},
            include=["documents", "metadatas", "distances"],
        )
    except Exception:
        results = {}

    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    distances = results.get("distances", [])

    # Priority 2: Fallback query without filter if no active match
    if not documents or not documents[0]:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])
        distances = results.get("distances", [])

    if not documents or not documents[0]:
        return []

    retrieved_chunks = []

    q_lower = normalize_query_tokens_for_matching(query_text)

    for document, metadata, distance in zip(
        documents[0],
        metadatas[0],
        distances[0],
    ):
        final_dist = distance
        if q_lower and metadata and metadata.get("filename"):
            fname_lower = metadata["filename"].lower()
            # If query explicitly matches filename terms (e.g. aiml, ds, timetable, calendar, ar25, 2yr/1sem)
            fname_tokens = [t for t in fname_lower.replace("-", " ").replace("_", " ").replace(".", " ").split() if len(t) > 1]
            matched_count = sum(1 for tok in fname_tokens if tok in q_lower)
            if matched_count >= 2:
                final_dist = min(final_dist, 0.45)
            elif matched_count == 1 and any(k in q_lower for k in ("table", "timetable", "schedule", "calendar", "regulations", "aiml", "ds")):
                final_dist = min(final_dist, 0.65)

        retrieved_chunks.append(
            {
                "text": document,
                "metadata": metadata,
                "distance": final_dist,
            }
        )

    return retrieved_chunks


def delete_document_chunks(document_id: str) -> None:
    try:
        collection.delete(
            where={
                "document_id": document_id,
            }
        )
    except Exception:
        pass

    try:
        vector_key = get_vector_storage_key(document_id)
        delete_file_from_storage(vector_key)
    except Exception:
        pass


def mark_document_chunks_inactive(document_id: str) -> None:
    """
    Mark chunks of a superseded document as inactive so they are not retrieved during normal RAG.
    """
    try:
        results = collection.get(where={"document_id": document_id})
        if results and results.get("ids"):
            ids = results["ids"]
            metadatas = results.get("metadatas", [])
            updated_metadatas = []
            for meta in metadatas:
                m = dict(meta) if meta else {}
                m["is_active"] = False
                updated_metadatas.append(m)

            collection.update(
                ids=ids,
                metadatas=updated_metadatas
            )
    except Exception:
        pass