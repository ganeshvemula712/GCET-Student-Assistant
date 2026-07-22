import chromadb


client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection(
    name="gcet_documents"
)


def store_chunks(
    chunks: list[dict],
    embeddings: list[list[float]],
) -> None:

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:

        metadata = chunk["metadata"]

        chunk_id = (
            f"{metadata['document_id']}_"
            f"{metadata['page']}_"
            f"{metadata['chunk_index']}"
        )

        ids.append(chunk_id)
        documents.append(chunk["text"])
        metadatas.append(metadata)

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )


def search_chunks(
    query_embedding: list[float],
    n_results: int = 3,
) -> list[dict]:

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

    for document, metadata, distance in zip(
        documents[0],
        metadatas[0],
        distances[0],
    ):
        retrieved_chunks.append(
            {
                "text": document,
                "metadata": metadata,
                "distance": distance,
            }
        )

    return retrieved_chunks
def delete_document_chunks(document_id: str) -> None:

    collection.delete(
        where={
            "document_id": document_id,
        }
    )