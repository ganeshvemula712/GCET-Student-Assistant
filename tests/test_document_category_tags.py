from unittest.mock import AsyncMock, patch
from backend.app.models.document import Document
from backend.app.services.documents import normalize_tags


def test_normalize_tags():
    assert normalize_tags(" JNTUH, R22, CSE, ") == "JNTUH, R22, CSE"
    assert normalize_tags("CSE, cse, CSE") == "CSE"
    assert normalize_tags("") == ""
    assert normalize_tags(None) == ""


def test_get_documents_with_category_filter(admin_client, db_session):
    doc1 = Document(
        document_id="cat-test-1",
        filename="syllabus.pdf",
        page_count=5,
        chunk_count=10,
        status="processed",
        category="Course Syllabus",
        tags="CSE, R22",
    )
    doc2 = Document(
        document_id="cat-test-2",
        filename="placements.pdf",
        page_count=2,
        chunk_count=5,
        status="processed",
        category="Placements",
        tags="2026, Salary",
    )
    db_session.add(doc1)
    db_session.add(doc2)
    db_session.commit()

    # 1. Unfiltered request
    res = admin_client.get("/documents")
    assert res.status_code == 200
    docs = res.json()
    assert len(docs) >= 2

    # 2. Filter by category = "Course Syllabus"
    res_syllabus = admin_client.get("/documents?category=Course+Syllabus")
    assert res_syllabus.status_code == 200
    data_syl = res_syllabus.json()
    assert len(data_syl) == 1
    assert data_syl[0]["document_id"] == "cat-test-1"
    assert data_syl[0]["category"] == "Course Syllabus"
    assert data_syl[0]["tags"] == "CSE, R22"

    # 3. Filter by category = "Placements"
    res_place = admin_client.get("/documents?category=Placements")
    assert res_place.status_code == 200
    data_place = res_place.json()
    assert len(data_place) == 1
    assert data_place[0]["document_id"] == "cat-test-2"
    assert data_place[0]["category"] == "Placements"


def test_existing_document_null_category_defaults_gracefully(admin_client, db_session):
    # Simulate an existing database record with NULL category and NULL tags
    legacy_doc = Document(
        document_id="legacy-doc-123",
        filename="legacy.pdf",
        page_count=3,
        chunk_count=6,
        status="processed",
        category=None,
        tags=None,
    )
    db_session.add(legacy_doc)
    db_session.commit()

    res = admin_client.get("/documents")
    assert res.status_code == 200
    data = res.json()
    matched = [d for d in data if d["document_id"] == "legacy-doc-123"]
    assert len(matched) == 1
    assert matched[0]["category"] == "General Academic"
    assert matched[0]["tags"] == ""


def test_upload_document_invalid_category_returns_400(admin_client):
    res = admin_client.post(
        "/documents/upload",
        data={"category": "Invalid Nonexistent Category"},
        files={
            "file": (
                "test.pdf",
                b"fake pdf content",
                "application/pdf",
            )
        },
    )
    assert res.status_code == 400
    msg = res.json().get("message") or res.json().get("detail", "")
    assert "Invalid category" in msg


def test_upload_document_valid_category_and_tags(admin_client):
    with patch(
        "backend.app.routers.documents.process_document",
        new_callable=AsyncMock,
    ) as mock_process_document:
        mock_process_document.return_value = {
            "id": 10,
            "document_id": "cat-upload-123",
            "filename": "regulations.pdf",
            "page_count": 8,
            "chunk_count": 16,
            "status": "processed",
            "version": 1,
            "is_active": True,
            "supersedes_id": None,
            "category": "Academic Regulations",
            "tags": "JNTUH, R22",
            "uploaded_at": "2026-08-15T16:00:00",
            "message": "Document processed successfully",
        }

        res = admin_client.post(
            "/documents/upload",
            data={
                "category": "Academic Regulations",
                "tags": " JNTUH, R22, ",
            },
            files={
                "file": (
                    "regulations.pdf",
                    b"fake pdf content",
                    "application/pdf",
                )
            },
        )

        assert res.status_code == 200
        data = res.json()
        assert data["category"] == "Academic Regulations"
        assert data["tags"] == "JNTUH, R22"
