from unittest.mock import AsyncMock, MagicMock, patch

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

    with patch("backend.app.services.documents.get_collection") as mock_coll:
        mock_instance = MagicMock()
        mock_instance.get.return_value = {"ids": [f"id_{i}" for i in range(25)]}
        mock_coll.return_value = mock_instance

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


def test_get_all_documents_restores_from_supabase_vector_json(
    admin_client,
    db_session,
):
    import json
    doc = Document(
        document_id="on_demand_restore_999",
        filename="ondemand.pdf",
        page_count=2,
        chunk_count=3,
        status="processed",
        is_active=True,
    )
    db_session.add(doc)
    db_session.commit()

    payload = {
        "document_id": "on_demand_restore_999",
        "ids": ["id1", "id2", "id3"],
        "documents": ["Text 1", "Text 2", "Text 3"],
        "metadatas": [{"document_id": "on_demand_restore_999"}, {"document_id": "on_demand_restore_999"}, {"document_id": "on_demand_restore_999"}],
        "embeddings": [[0.1] * 768, [0.2] * 768, [0.3] * 768],
    }
    payload_bytes = json.dumps(payload).encode("utf-8")

    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": []}  # ChromaDB missing vectors

    with patch("backend.app.services.documents.get_collection", return_value=mock_coll), \
         patch("backend.app.services.documents.download_file_from_storage", return_value=payload_bytes):

        response = admin_client.get("/documents")
        assert response.status_code == 200

        data = response.json()
        target = [d for d in data if d["document_id"] == "on_demand_restore_999"][0]
        assert target["status"] == "processed"
        assert target["chunk_count"] == 3
        assert target["is_active"] is True

        mock_coll.upsert.assert_called_once_with(
            ids=payload["ids"],
            documents=payload["documents"],
            metadatas=payload["metadatas"],
            embeddings=payload["embeddings"],
        )