import pytest
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from backend.app.models.document import Document
from backend.app.services.documents import get_documents, reindex_document
from backend.app.services.ocr import GeminiQuotaExhaustedError
from backend.app.services.startup import sync_chromadb_with_postgres


def test_missing_chromadb_vectors_returns_indexing_required(db_session: Session):
    """Test that get_documents returns indexing_required and chunk_count=0 when ChromaDB has 0 vectors."""
    doc = Document(
        document_id="doc_missing_vectors_123",
        filename="test_missing.pdf",
        page_count=5,
        chunk_count=102,  # Historical DB chunk count
        status="processed",
        version=1,
        is_active=True,
    )
    db_session.add(doc)
    db_session.commit()

    with patch("backend.app.services.documents.get_collection") as mock_coll:
        mock_instance = MagicMock()
        mock_instance.get.return_value = {"ids": []}  # 0 vectors in ChromaDB
        mock_coll.return_value = mock_instance

        docs = get_documents(db_session)
        target = next(d for d in docs if d["document_id"] == "doc_missing_vectors_123")

        # Response representation must be updated
        assert target["status"] == "indexing_required"
        assert target["chunk_count"] == 0
        assert target["is_active"] is False

        # Database record historical chunk_count must remain untouched
        db_doc = db_session.query(Document).filter(Document.document_id == "doc_missing_vectors_123").first()
        assert db_doc.chunk_count == 102


def test_reindex_document_success(db_session: Session):
    """Test successful re-indexing of a document from Supabase Storage."""
    doc = Document(
        document_id="doc_reindex_success_456",
        filename="reindex_test.pdf",
        page_count=2,
        chunk_count=0,
        status="indexing_required",
        version=1,
        is_active=False,
    )
    db_session.add(doc)
    db_session.commit()

    mock_pages = (2, [(1, "Extracted page 1 text"), (2, "Extracted page 2 text")])
    mock_embeddings = [[0.1] * 768, [0.2] * 768]

    with patch("backend.app.services.documents.download_file_from_storage", return_value=b"%PDF-sample"), \
         patch("backend.app.services.documents.extract_document_pages", return_value=mock_pages), \
         patch("backend.app.services.documents.generate_embeddings", return_value=mock_embeddings), \
         patch("backend.app.services.documents.store_chunks") as mock_store:

        res = reindex_document("doc_reindex_success_456", db_session)
        assert res["status"] == "processed"
        assert res["is_active"] is True
        assert res["chunk_count"] > 0
        mock_store.assert_called_once()

        db_doc = db_session.query(Document).filter(Document.document_id == "doc_reindex_success_456").first()
        assert db_doc.status == "processed"
        assert db_doc.is_active is True


def test_reindex_document_missing_supabase_file(db_session: Session):
    """Test re-indexing when file is missing from Supabase Storage returns 400."""
    doc = Document(
        document_id="doc_missing_file_789",
        filename="missing_file.pdf",
        page_count=1,
        chunk_count=0,
        status="indexing_required",
        version=1,
        is_active=False,
    )
    db_session.add(doc)
    db_session.commit()

    with patch("backend.app.services.documents.download_file_from_storage", return_value=None):
        with pytest.raises(Exception) as exc_info:
            reindex_document("doc_missing_file_789", db_session)
        assert "400" in str(exc_info.value) or "not found" in str(exc_info.value)


def test_reindex_document_gemini_quota_exhaustion(db_session: Session):
    """Test re-indexing when Gemini quota is exhausted returns 429."""
    doc = Document(
        document_id="doc_quota_exhausted_999",
        filename="quota_test.pdf",
        page_count=1,
        chunk_count=0,
        status="indexing_required",
        version=1,
        is_active=False,
    )
    db_session.add(doc)
    db_session.commit()

    with patch("backend.app.services.documents.download_file_from_storage", return_value=b"%PDF-sample"), \
         patch("backend.app.services.documents.extract_document_pages", side_effect=GeminiQuotaExhaustedError("Quota exhausted")):
        with pytest.raises(Exception) as exc_info:
            reindex_document("doc_quota_exhausted_999", db_session)
        assert "429" in str(exc_info.value) or "quota" in str(exc_info.value).lower()


def test_self_healing_continues_after_one_document_failure(db_session: Session):
    """Test that startup self-healing loop continues to subsequent documents if one document fails."""
    doc1 = Document(
        document_id="heal_doc_fail_1",
        filename="fail1.pdf",
        page_count=1,
        chunk_count=0,
        status="indexing_required",
        is_active=True,
    )
    doc2 = Document(
        document_id="heal_doc_pass_2",
        filename="pass2.pdf",
        page_count=1,
        chunk_count=0,
        status="indexing_required",
        is_active=True,
    )
    db_session.add_all([doc1, doc2])
    db_session.commit()

    def mock_download(key):
        if "heal_doc_fail_1" in key:
            return None  # Fails
        return b"%PDF-sample2"  # Passes

    mock_pages = (1, [(1, "Valid text for pass2")])

    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": []}  # Initially 0 vectors for both

    with patch("backend.app.services.startup.SessionLocal", return_value=db_session), \
         patch("backend.app.services.startup.get_collection", return_value=mock_coll), \
         patch("backend.app.services.startup.download_file_from_storage", side_effect=mock_download), \
         patch("backend.app.services.startup.extract_document_pages", return_value=mock_pages), \
         patch("backend.app.services.startup.generate_embeddings", return_value=[[0.1] * 768]), \
         patch("backend.app.services.startup.store_chunks"):

        sync_chromadb_with_postgres()

        # Verification: doc2 must have processed despite doc1 failing
        d2 = db_session.query(Document).filter(Document.document_id == "heal_doc_pass_2").first()
        assert d2.status == "processed"
        assert d2.is_active is True


def test_concurrent_reindex_lock_rejection(db_session: Session):
    """Test that concurrent re-indexing on the same document raises 409 Conflict."""
    from backend.app.services.documents import acquire_reindex_lock, release_reindex_lock

    doc_id = "doc_lock_test_100"
    doc = Document(
        document_id=doc_id,
        filename="lock_test.pdf",
        page_count=1,
        chunk_count=0,
        status="indexing_required",
        is_active=False,
    )
    db_session.add(doc)
    db_session.commit()

    # Manually acquire lock for doc_id
    assert acquire_reindex_lock(doc_id) is True

    try:
        # Subsequent reindex attempt on same doc_id must fail with 409
        with pytest.raises(Exception) as exc_info:
            reindex_document(doc_id, db_session)
        assert "409" in str(exc_info.value) or "currently being indexed" in str(exc_info.value)
    finally:
        release_reindex_lock(doc_id)
