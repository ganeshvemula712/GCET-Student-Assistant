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


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Convert a list of text strings into numerical vectors using Google Gemini Embeddings API (models/gemini-embedding-2).
    Supports single queries and document chunk embedding.
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
        for attempt in range(1, MAX_RETRIES + 1):
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
                    wait_sec = 35
                    logger.warning(
                        f"[GEMINI EMBEDDINGS RATE LIMIT] Rate limited (Attempt {attempt}/{MAX_RETRIES}). Waiting {wait_sec}s for quota window reset..."
                    )
                    time.sleep(wait_sec)
                else:
                    logger.error(f"Gemini API embedding error: {api_err}")
                    raise api_err

        if vector is not None:
            embeddings.append(vector)

        time.sleep(1.0) # Paced to stay well under Gemini 100 RPM quota limit

    return embeddings