def chunk_text(
    text: str,
    filename: str,
    page_number: int,
    document_id: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[dict]:

    chunks = []
    start = 0
    chunk_index = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(
            {
                "text": chunk,
                "metadata": {
                    "filename": filename,
                    "document_id": document_id,
                    "page": page_number,
                    "chunk_index": chunk_index,
                },
            }
        )

        start += chunk_size - chunk_overlap

        chunk_index += 1

    return chunks