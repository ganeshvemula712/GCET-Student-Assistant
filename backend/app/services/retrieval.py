import logging
from backend.app.services.embeddings import generate_query_embedding
from backend.app.services.vector_store import search_chunks

logger = logging.getLogger("uvicorn")


class RetrievalServiceError(Exception):
    """Raised when vector retrieval service cannot process query embeddings (e.g., rate limits)."""
    pass


def retrieve_relevant_chunks(
    question: str,
    n_results: int = 3,
):
    """
    Convert the user's question into an embedding with LRU caching
    and retrieve the most relevant chunks from ChromaDB.
    Fast-fails on rate limits for single chat queries.
    Raises RetrievalServiceError if query embedding fails.
    """
    try:
        query_embedding = generate_query_embedding(question)
        if not query_embedding:
            raise RetrievalServiceError("Vector embedding generation returned no vector.")

        relevant_chunks = search_chunks(
            query_embedding=query_embedding,
            n_results=n_results,
            query_text=question,
        )
        return relevant_chunks

    except RetrievalServiceError:
        raise
    except Exception as err:
        logger.warning(
            f"[RETRIEVAL SERVICE] Vector embedding generation unavailable for query: {err}"
        )
        raise RetrievalServiceError(
            "GCET Knowledge Base retrieval is temporarily unavailable due to embedding API rate limits."
        ) from err