from backend.app.services.embeddings import generate_embeddings
from backend.app.services.vector_store import search_chunks


def retrieve_relevant_chunks(
    question: str,
    n_results: int = 3,
):
    """
    Convert the user's question into an embedding
    and retrieve the most relevant chunks from ChromaDB.
    """

    query_embedding = generate_embeddings([question])[0]

    relevant_chunks = search_chunks(
        query_embedding=query_embedding,
        n_results=n_results,
    )

    return relevant_chunks