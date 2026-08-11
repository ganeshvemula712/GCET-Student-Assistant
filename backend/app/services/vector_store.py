import chromadb


client = chromadb.PersistentClient(path="chroma_db")


def get_collection():
    return client.get_or_create_collection(name="gcet_documents")


collection = get_collection()


def store_chunks(
    chunks: list[dict],
    embeddings: list[list[float]],
) -> None:

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


def search_chunks(
    query_embedding: list[float],
    n_results: int = 3,
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
    try:
        collection.delete(
            where={
                "document_id": document_id,
            }
        )
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