import logging
import time
from backend.app.services.gemini import client

logger = logging.getLogger("uvicorn")

EMBEDDING_MODEL = "models/gemini-embedding-2"
MAX_RETRIES = 10


def get_embedding_model():
    """
    Compatibility stub for legacy callers.
    """
    return EMBEDDING_MODEL


def generate_embeddings(
    texts: list[str],
    max_retries: int = MAX_RETRIES,
    retry_delay: float = 35.0,
) -> list[list[float]]:
    """
    Convert a list of text strings into numerical vectors using Google Gemini Embeddings API (models/gemini-embedding-2).
    Supports single queries (fast fail with max_retries=1) and document chunk embedding (default max_retries=10).
    Returns 3072-dimensional floating point vectors.
    """
    if not texts:
        return []

    cleaned_texts = [t.strip() if isinstance(t, str) else str(t) for t in texts]

    embeddings: list[list[float]] = []

    for text_item in cleaned_texts:
        if not text_item:
            text_item = "empty chunk"

        vector = None
        for attempt in range(1, max_retries + 1):
            try:
                response = client.models.embed_content(
                    model=EMBEDDING_MODEL,
                    contents=text_item,
                )
                if response and response.embeddings:
                    vector = list(response.embeddings[0].values)
                break
            except Exception as api_err:
                err_msg = str(api_err)
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                    if attempt < max_retries:
                        logger.warning(
                            f"[GEMINI EMBEDDINGS RATE LIMIT] Rate limited (Attempt {attempt}/{max_retries}). Waiting {retry_delay}s for quota window reset..."
                        )
                        time.sleep(retry_delay)
                    else:
                        logger.error(
                            f"[GEMINI EMBEDDINGS RATE LIMIT] Max retries ({max_retries}) reached for embedding generation: {api_err}"
                        )
                        raise api_err
        if vector is not None:
            embeddings.append(vector)

        if len(cleaned_texts) > 1:
            time.sleep(1.0) # Paced to stay well under Gemini 100 RPM quota limit

    return embeddings

from functools import lru_cache

QUERY_CACHE_SIZE = 300


@lru_cache(maxsize=QUERY_CACHE_SIZE)
def _cached_query_embedding(normalized_query: str) -> tuple[float, ...]:
    """
    Internal bounded LRU-cached helper for single query embeddings.
    Returns tuple of floats for hashability and immutability.
    """
    vectors = generate_embeddings(
        [normalized_query],
        max_retries=1,
        retry_delay=2.0,
    )
    if not vectors:
        raise ValueError("Embedding generation returned empty result")
    return tuple(vectors[0])


def generate_query_embedding(question: str) -> list[float]:
    """
    Convert a single chat query string into a 3072D vector with LRU caching.
    Normalizes query string (strip leading/trailing whitespace and lowercase) for cache lookup.
    """
    if not question or not question.strip():
        return []

    normalized_key = question.strip().lower()
    tuple_vector = _cached_query_embedding(normalized_key)
    return list(tuple_vector)