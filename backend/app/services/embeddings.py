from sentence_transformers import SentenceTransformer


embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Convert a list of text chunks into numerical vectors.
    """

    embeddings = embedding_model.encode(texts)

    return embeddings.tolist()