from hashlib import sha256
from io import BytesIO

import pymupdf

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.app.models.document import Document
from backend.app.services.embeddings import generate_embeddings
from backend.app.services.text_processing import chunk_text
from backend.app.services.vector_store import (
    delete_document_chunks,
    store_chunks,
)


async def process_document(
    file: UploadFile,
    db: Session,
) -> dict:

    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed",
        )

    # Read uploaded file
    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded PDF is empty",
        )

    # Generate unique document ID
    document_id = sha256(content).hexdigest()

    # Check whether document already exists
    existing_document = (
        db.query(Document)
        .filter(Document.document_id == document_id)
        .first()
    )

    if existing_document:
        raise HTTPException(
            status_code=409,
            detail="This document has already been uploaded",
        )

    # Open PDF
    try:
        pdf_document = pymupdf.open(
            stream=BytesIO(content),
            filetype="pdf",
        )

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid or corrupted PDF file",
        )

    all_chunks = []
    total_character_count = 0

    # Process PDF page-by-page
    for page_index, page in enumerate(pdf_document):

        page_text = page.get_text()

        if not page_text.strip():
            continue

        total_character_count += len(page_text)

        page_number = page_index + 1

        page_chunks = chunk_text(
            text=page_text,
            filename=file.filename,
            page_number=page_number,
            document_id=document_id,
        )

        all_chunks.extend(page_chunks)

    page_count = len(pdf_document)

    pdf_document.close()

    # Ensure document contains text
    if not all_chunks:
        raise HTTPException(
            status_code=400,
            detail="No extractable text found in the PDF",
        )

    # Generate embeddings
    texts = [
        chunk["text"]
        for chunk in all_chunks
    ]

    embeddings = generate_embeddings(texts)

    # Store vectors in ChromaDB
    store_chunks(
        chunks=all_chunks,
        embeddings=embeddings,
    )

    # Create PostgreSQL document record
    new_document = Document(
        document_id=document_id,
        filename=file.filename,
        page_count=page_count,
        chunk_count=len(all_chunks),
        status="processed",
    )

    try:
        db.add(new_document)
        db.commit()
        db.refresh(new_document)

    except Exception:
        db.rollback()

        # Remove vectors if PostgreSQL storage fails
        delete_document_chunks(document_id)

        raise HTTPException(
            status_code=500,
            detail="Failed to save document",
        )

    return {
        "id": new_document.id,
        "document_id": new_document.document_id,
        "filename": new_document.filename,
        "page_count": new_document.page_count,
        "chunk_count": new_document.chunk_count,
        "status": new_document.status,
        "uploaded_at": new_document.uploaded_at,
        "message": "Document processed and stored successfully",
    }


def get_documents(
    db: Session,
) -> list[Document]:

    documents = db.query(Document).all()

    return documents


def remove_document(
    document_id: str,
    db: Session,
) -> dict:

    document = (
        db.query(Document)
        .filter(Document.document_id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    filename = document.filename

    try:
        delete_document_chunks(document_id)

        db.delete(document)

        db.commit()

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(error)}",
        )

    return {
        "message": "Document deleted successfully",
        "document_id": document_id,
        "filename": filename,
    }