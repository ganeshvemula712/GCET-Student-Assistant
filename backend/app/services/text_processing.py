def chunk_text(
    text: str,
    filename: str,
    page_number: int,
    document_id: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    category: str | None = None,
    tags: str | None = None,
) -> list[dict]:

    chunks = []
    start = 0
    chunk_index = 0

    header = f"Document: {filename}"
    if category:
        header += f" | Category: {category}"
    if tags:
        header += f" | Tags: {tags}"
    header += "\n\n"

    while start < len(text):

        end = start + chunk_size

        raw_chunk = text[start:end]
        chunk_content = f"{header}{raw_chunk}"

        chunks.append(
            {
                "text": chunk_content,
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