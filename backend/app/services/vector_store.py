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


import re

BRANCHES = {
    "ds": ["ds", "data science"],
    "aiml": ["aiml", "ai ml", "ai&ml", "ai and ml", "artificial intelligence"],
    "cs": ["cs", "cse", "cyber security", "cybersecurity"],
    "ece": ["ece", "electronics"],
    "eee": ["eee", "electrical"],
    "mech": ["mech", "mechanical"],
}


def extract_query_entities(query_text: str | None) -> dict:
    if not query_text:
        return {"branch": None, "section": None, "year": None, "semester": None}

    q_lower = query_text.lower().strip()

    # 1. Combined branch-section pattern (e.g. "ds-d", "aiml-d", "cs-a", "aiml a", "ds d")
    found_branch = None
    found_section = None

    combined_match = re.search(r"\b(ds|aiml|cs|cse)\s*[-_\s]\s*([abcd])\b", q_lower)
    if combined_match:
        b_raw, s_raw = combined_match.group(1), combined_match.group(2)
        found_branch = "cs" if b_raw in ("cs", "cse") else b_raw
        found_section = s_raw
    else:
        for canonical, aliases in BRANCHES.items():
            for alias in aliases:
                if re.search(r"\b" + re.escape(alias) + r"\b", q_lower):
                    found_branch = canonical
                    break
            if found_branch:
                break

        sec_match = re.search(r"\b(?:section|sec|sec-)\s*([abcd])\b|\b([abcd])\s*section\b", q_lower)
        if sec_match:
            found_section = sec_match.group(1) or sec_match.group(2)

    found_year = None
    year_match = re.search(r"\b(1st|2nd|3rd|4th|1|2|3|4)\s*(?:st|nd|rd|th)?\s*(?:yr|year|b\.?tech|btech)?\b", q_lower)
    if year_match:
        y_str = year_match.group(1).replace("st", "").replace("nd", "").replace("rd", "").replace("th", "")
        if y_str in ("1", "2", "3", "4"):
            found_year = y_str

    found_sem = None
    sem_match = re.search(r"\b(1st|2nd|1|2)\s*(?:st|nd)?\s*(?:sem|semester)\b", q_lower)
    if sem_match:
        s_str = sem_match.group(1).replace("st", "").replace("nd", "")
        if s_str in ("1", "2"):
            found_sem = s_str

    return {
        "branch": found_branch,
        "section": found_section,
        "year": found_year,
        "semester": found_sem,
        "raw_query": query_text,
    }


def score_chunk_metadata_alignment(meta: dict, entities: dict, raw_distance: float, text: str = "") -> float:
    if not meta or not any(entities.values()):
        return raw_distance

    fname = (meta.get("filename") or "").lower()
    tags = (meta.get("tags") or "").lower()
    text_snippet = (text[:300] if text else "").lower()
    combined_text = f"{fname} {tags} {text_snippet}"

    q_branch = entities["branch"]
    q_section = entities["section"]
    q_year = entities["year"]

    distance_modifier = 0.0

    if q_branch:
        doc_branch = None
        if "ds" in combined_text or "data science" in combined_text:
            doc_branch = "ds"
        elif "aiml" in combined_text or "ai ml" in combined_text or "ai&ml" in combined_text:
            doc_branch = "aiml"
        elif "cs" in combined_text or "cyber security" in combined_text:
            doc_branch = "cs"
        elif "mech" in combined_text or "mechanical" in combined_text:
            doc_branch = "mech"

        if doc_branch == q_branch:
            distance_modifier -= 0.20
        elif doc_branch and doc_branch != q_branch:
            distance_modifier += 0.35

    if q_section:
        sec_pattern = r"\b" + re.escape(q_section) + r"\b|\bsec[-_\s]*" + re.escape(q_section) + r"\b"
        if re.search(sec_pattern, combined_text):
            distance_modifier -= 0.10
        else:
            for other_sec in ("a", "b", "c", "d"):
                if other_sec != q_section and re.search(r"\bsec[-_\s]*" + other_sec + r"\b|\b" + other_sec + r"\s*section\b", combined_text):
                    distance_modifier += 0.15
                    break

    if q_year:
        year_tokens = {
            "1": ["1st", "i-btech", "1 year", "1yr"],
            "2": ["2nd", "ii-btech", "2 year", "2yr"],
            "3": ["3rd", "iii-btech", "3 year", "3yr"],
            "4": ["4th", "iv-btech", "4 year", "4yr"],
        }
        y_tokens = year_tokens.get(q_year, [])
        if any(tok in combined_text for tok in y_tokens):
            distance_modifier -= 0.05

    if q_branch and q_section:
        combo_target = f"{q_branch}-{q_section}"
        combo_target_space = f"{q_branch} {q_section}"
        combo_target_underscore = f"{q_branch}_{q_section}"

        if combo_target in combined_text or combo_target_space in combined_text or combo_target_underscore in combined_text:
            distance_modifier -= 0.35
        else:
            for other_b in ("aiml", "ds", "cs", "cse", "ece", "eee", "mech"):
                if other_b != q_branch and (f"{other_b}-{q_section}" in combined_text or f"{other_b} {q_section}" in combined_text or f"{other_b}_{q_section}" in combined_text):
                    distance_modifier += 0.55
                    break

    # Timetable-specific document prioritization
    q_is_timetable = bool(re.search(r"\b(timetable|time table|schedule|tt)\b", (entities.get("raw_query") or "").lower()))
    if q_is_timetable:
        if any(tok in combined_text for tok in ("timetable", "time table", "tt")):
            distance_modifier -= 0.25
        elif any(tok in combined_text for tok in ("academic calendar", "mid examination", "syllabus")):
            distance_modifier += 0.40

    final_dist = max(0.0, raw_distance + distance_modifier)
    return final_dist


def normalize_query_tokens_for_matching(query_text: str | None) -> str:
    if not query_text:
        return ""
    q_lower = query_text.lower().strip()
    for variant, canonical in SPELLING_NORM_MAP.items():
        q_lower = q_lower.replace(variant, canonical)
    return q_lower


def deduplicate_and_rank_chunks(candidate_chunks: list[dict], max_results: int = 3) -> list[dict]:
    """
    Filter duplicate and near-duplicate text chunks while preserving highest relevance,
    complete source metadata (filename, page, etc.), and preventing context pollution.
    """
    if not candidate_chunks:
        return []

    sorted_chunks = sorted(candidate_chunks, key=lambda x: x.get("distance", 2.0))
    deduped: list[dict] = []
    seen_texts: set[str] = set()
    page_chunk_counts: dict[tuple[str, int], int] = {}

    for chunk in sorted_chunks:
        text = chunk.get("text", "").strip()
        if not text:
            continue

        # Normalize text snippet for exact & near-duplicate comparison
        norm_snippet = " ".join(text.lower().split()[:30])
        if norm_snippet in seen_texts:
            continue

        meta = chunk.get("metadata") or {}
        fname = meta.get("filename", "")
        page = meta.get("page", 1)
        doc_page_key = (fname, page)

        # Cap max chunks from the exact same (filename, page) to 2 to prevent single-page context flood
        if page_chunk_counts.get(doc_page_key, 0) >= 2:
            continue

        seen_texts.add(norm_snippet)
        page_chunk_counts[doc_page_key] = page_chunk_counts.get(doc_page_key, 0) + 1
        deduped.append(chunk)

        if len(deduped) >= max_results:
            break

    return deduped


def search_chunks(
    query_embedding: list[float],
    n_results: int = 3,
    query_text: str | None = None,
) -> list[dict]:

    coll = get_collection()
    # Expand initial candidate pool from ChromaDB so entity re-ranking sees all candidate documents
    candidate_limit = max(n_results * 4, 10)

    try:
        results = coll.query(
            query_embeddings=[query_embedding],
            n_results=candidate_limit,
            where={"is_active": True},
            include=["documents", "metadatas", "distances"],
        )
    except Exception:
        results = {}

    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    distances = results.get("distances", [])

    if not documents or not documents[0]:
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=candidate_limit,
                include=["documents", "metadatas", "distances"],
            )
            documents = results.get("documents", [])
            metadatas = results.get("metadatas", [])
            distances = results.get("distances", [])
        except Exception:
            pass

    if not documents or not documents[0]:
        return []

    entities = extract_query_entities(query_text)
    candidate_chunks = []

    for document, metadata, distance in zip(
        documents[0],
        metadatas[0],
        distances[0],
    ):
        adjusted_dist = score_chunk_metadata_alignment(metadata, entities, distance, document)
        candidate_chunks.append(
            {
                "text": document,
                "metadata": metadata,
                "distance": adjusted_dist,
                "raw_distance": distance,
            }
        )

    # Return top n_results after entity-aware re-ranking and deduplication
    return deduplicate_and_rank_chunks(candidate_chunks, max_results=n_results)


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