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

    q_lower = query_text.lower().strip() if query_text else ""

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