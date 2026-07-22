from unittest.mock import AsyncMock, patch

from backend.app.models.document import Document


def test_get_all_documents_empty(
    admin_client,
):

    response = admin_client.get("/documents")

    assert response.status_code == 200

    assert response.json() == []


def test_get_all_documents_with_data(
    admin_client,
    db_session,
):

    document = Document(
        document_id="test-document-123",
        filename="test-document.pdf",
        page_count=10,
        chunk_count=25,
        status="processed",
    )

    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    response = admin_client.get("/documents")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["document_id"] == "test-document-123"
    assert data[0]["filename"] == "test-document.pdf"
    assert data[0]["page_count"] == 10
    assert data[0]["chunk_count"] == 25
    assert data[0]["status"] == "processed"


def test_delete_document(
    admin_client,
    db_session,
):

    document = Document(
        document_id="delete-test-123",
        filename="delete-test.pdf",
        page_count=5,
        chunk_count=15,
        status="processed",
    )

    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    with patch(
        "backend.app.services.documents.delete_document_chunks"
    ) as mock_delete_chunks:

        response = admin_client.delete(
            "/documents/delete-test-123"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Document deleted successfully"
    assert data["document_id"] == "delete-test-123"
    assert data["filename"] == "delete-test.pdf"

    mock_delete_chunks.assert_called_once_with(
        "delete-test-123"
    )

    db_session.expire_all()

    deleted_document = (
        db_session.query(Document)
        .filter(
            Document.document_id == "delete-test-123"
        )
        .first()
    )

    assert deleted_document is None


def test_delete_document_not_found(
    admin_client,
):

    response = admin_client.delete(
        "/documents/non-existent-document"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 404
    assert data["message"] == "Document not found"
    assert data["path"] == "/documents/non-existent-document"
    assert "timestamp" in data

def test_upload_document(
    admin_client,
):

    with patch(
        "backend.app.routers.documents.process_document",
        new_callable=AsyncMock,
    ) as mock_process_document:

        mock_process_document.return_value = {
            "id": 1,
            "document_id": "upload-test-123",
            "filename": "test.pdf",
            "page_count": 5,
            "chunk_count": 10,
            "status": "processed",
            "uploaded_at": "2026-07-14T10:00:00",
            "message": "Document processed and stored successfully",
        }

        response = admin_client.post(
            "/documents/upload",
            files={
                "file": (
                    "test.pdf",
                    b"fake pdf content",
                    "application/pdf",
                )
            },
        )

        mock_process_document.assert_awaited_once()

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"] == "upload-test-123"
    assert data["filename"] == "test.pdf"
    assert data["page_count"] == 5
    assert data["chunk_count"] == 10
    assert data["status"] == "processed"
    assert (
        data["message"]
        == "Document processed and stored successfully"
    )