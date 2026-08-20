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


def test_self_healing_preserves_previously_processed_state_on_recovery_failure(db_session: Session):
    """TEST A: Previously processed document preserves PostgreSQL state when recovery temporarily fails."""
    doc = Document(
        document_id="test_a_processed_doc",
        filename="processed_sample.pdf",
        page_count=5,
        chunk_count=15,
        status="processed",
        version=1,
        is_active=True,
    )
    db_session.add(doc)
    db_session.commit()

    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": []}  # Missing from ChromaDB

    with patch("backend.app.services.startup.SessionLocal", return_value=db_session), \
         patch("backend.app.services.startup.get_collection", return_value=mock_coll), \
         patch("backend.app.services.startup.download_file_from_storage", return_value=b"%PDF-sample"), \
         patch("backend.app.services.startup._reindex_document_from_bytes", return_value=0):  # Simulated recovery failure

        sync_chromadb_with_postgres()

        saved_doc = db_session.query(Document).filter(Document.document_id == "test_a_processed_doc").first()
        assert saved_doc.status == "processed"
        assert saved_doc.chunk_count == 15
        assert saved_doc.is_active is True


def test_self_healing_unprocessed_document_remains_indexing_required_on_failure(db_session: Session):
    """TEST B: Unprocessed document remains indexing_required when recovery fails."""
    doc = Document(
        document_id="test_b_unprocessed_doc",
        filename="unprocessed_sample.jpeg",
        page_count=1,
        chunk_count=0,
        status="indexing_required",
        version=1,
        is_active=False,
    )
    db_session.add(doc)
    db_session.commit()

    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": []}

    with patch("backend.app.services.startup.SessionLocal", return_value=db_session), \
         patch("backend.app.services.startup.get_collection", return_value=mock_coll), \
         patch("backend.app.services.startup.download_file_from_storage", return_value=b"image-bytes"), \
         patch("backend.app.services.startup._reindex_document_from_bytes", return_value=0):

        sync_chromadb_with_postgres()

        saved_doc = db_session.query(Document).filter(Document.document_id == "test_b_unprocessed_doc").first()
        assert saved_doc.status == "indexing_required"
        assert saved_doc.chunk_count == 0
        assert saved_doc.is_active is False


def test_self_healing_processed_document_updates_chunk_count_on_successful_recovery(db_session: Session):
    """TEST C: Previously processed document updates vector count when recovery succeeds."""
    doc = Document(
        document_id="test_c_recovery_success_doc",
        filename="recovery_success.pdf",
        page_count=3,
        chunk_count=10,
        status="processed",
        version=1,
        is_active=True,
    )
    db_session.add(doc)
    db_session.commit()

    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": []}

    with patch("backend.app.services.startup.SessionLocal", return_value=db_session), \
         patch("backend.app.services.startup.get_collection", return_value=mock_coll), \
         patch("backend.app.services.startup.download_file_from_storage", return_value=b"%PDF-sample"), \
         patch("backend.app.services.startup._reindex_document_from_bytes", return_value=12):

        sync_chromadb_with_postgres()

        saved_doc = db_session.query(Document).filter(Document.document_id == "test_c_recovery_success_doc").first()
        assert saved_doc.status == "processed"
        assert saved_doc.chunk_count == 12
        assert saved_doc.is_active is True


def test_vector_backup_created_on_store_chunks():
    """TEST A: store_chunks serializes and uploads vector payload JSON to Supabase Storage."""
    import json
    chunks = [
        {
            "text": "Sample chunk text for persistence test.",
            "metadata": {"document_id": "doc_backup_101", "page": 1, "chunk_index": 0, "is_active": True}
        }
    ]
    embeddings = [[0.123456789, 0.987654321]]

    mock_coll = MagicMock()
    with patch("backend.app.services.vector_store.get_collection", return_value=mock_coll), \
         patch("backend.app.services.vector_store.upload_file_to_storage") as mock_upload:

        from backend.app.services.vector_store import store_chunks
        store_chunks(chunks, embeddings)

        mock_coll.upsert.assert_called_once()
        mock_upload.assert_called_once()

        call_args = mock_upload.call_args
        content = call_args[1]["content"] if "content" in call_args[1] else call_args[0][0]
        object_key = call_args[1]["object_key"] if "object_key" in call_args[1] else call_args[0][1]

        assert object_key == "vectors/doc_backup_101.json"
        payload = json.loads(content.decode("utf-8"))
        assert payload["document_id"] == "doc_backup_101"
        assert payload["ids"] == ["doc_backup_101_1_0"]
        assert payload["documents"] == ["Sample chunk text for persistence test."]
        assert payload["metadatas"][0]["document_id"] == "doc_backup_101"
        assert len(payload["embeddings"]) == 1
        assert abs(payload["embeddings"][0][0] - 0.123456789) < 1e-6


def test_restore_from_supabase_vector_json_avoids_gemini_calls(db_session: Session):
    """TEST B: Startup self-healing restores vectors directly from Supabase vector JSON without calling Gemini Embeddings API."""
    import json
    doc = Document(
        document_id="doc_json_restore_202",
        filename="json_restore.pdf",
        page_count=1,
        chunk_count=2,
        status="processed",
        version=1,
        is_active=True,
    )
    db_session.add(doc)
    db_session.commit()

    payload = {
        "document_id": "doc_json_restore_202",
        "ids": ["doc_json_restore_202_1_0", "doc_json_restore_202_1_1"],
        "documents": ["Text chunk 1", "Text chunk 2"],
        "metadatas": [{"document_id": "doc_json_restore_202", "page": 1, "chunk_index": 0}, {"document_id": "doc_json_restore_202", "page": 1, "chunk_index": 1}],
        "embeddings": [[0.1] * 768, [0.2] * 768]
    }
    payload_bytes = json.dumps(payload).encode("utf-8")

    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": []}  # ChromaDB empty on boot

    with patch("backend.app.services.startup.SessionLocal", return_value=db_session), \
         patch("backend.app.services.startup.get_collection", return_value=mock_coll), \
         patch("backend.app.services.startup.download_file_from_storage", return_value=payload_bytes), \
         patch("backend.app.services.startup.generate_embeddings") as mock_gemini_emb:

        sync_chromadb_with_postgres()

        mock_coll.upsert.assert_called_once_with(
            ids=payload["ids"],
            documents=payload["documents"],
            metadatas=payload["metadatas"],
            embeddings=payload["embeddings"],
        )
        # CRITICAL ASSERTION: Gemini Embeddings API was NOT called!
        mock_gemini_emb.assert_not_called()

        saved_doc = db_session.query(Document).filter(Document.document_id == "doc_json_restore_202").first()
        assert saved_doc.status == "processed"
        assert saved_doc.chunk_count == 2
        assert saved_doc.is_active is True


def test_invalid_vector_json_bypassed_and_preserves_change1_state(db_session: Session):
    """TEST C: Malformed vector JSON payload is rejected and does not corrupt database or crash startup."""
    doc = Document(
        document_id="doc_invalid_json_303",
        filename="corrupt_restore.pdf",
        page_count=1,
        chunk_count=5,
        status="processed",
        version=1,
        is_active=True,
    )
    db_session.add(doc)
    db_session.commit()

    malformed_json_bytes = b'{"document_id": "wrong_id", "ids": [123]}'  # Mismatched ID & structure

    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": []}

    with patch("backend.app.services.startup.SessionLocal", return_value=db_session), \
         patch("backend.app.services.startup.get_collection", return_value=mock_coll), \
         patch("backend.app.services.startup.download_file_from_storage", return_value=malformed_json_bytes), \
         patch("backend.app.services.startup._reindex_document_from_bytes", return_value=0):

        sync_chromadb_with_postgres()

        # ChromaDB upsert must NOT have been called with corrupt data
        mock_coll.upsert.assert_not_called()

        # Change #1 state protection preserves processed state
        saved_doc = db_session.query(Document).filter(Document.document_id == "doc_invalid_json_303").first()
        assert saved_doc.status == "processed"
        assert saved_doc.chunk_count == 5


def test_delete_document_chunks_removes_vector_json():
    """TEST D: delete_document_chunks removes vectors from ChromaDB AND deletes vector payload JSON from Supabase Storage."""
    mock_coll = MagicMock()
    with patch("backend.app.services.vector_store.collection", mock_coll), \
         patch("backend.app.services.vector_store.delete_file_from_storage") as mock_delete:

        from backend.app.services.vector_store import delete_document_chunks
        delete_document_chunks("doc_delete_404")

        mock_coll.delete.assert_called_once_with(where={"document_id": "doc_delete_404"})
        mock_delete.assert_called_once_with("vectors/doc_delete_404.json")


def test_reindex_replaces_vector_payload_in_storage(db_session: Session):
    """TEST E: Re-indexing a document replaces vector payload JSON in Supabase Storage."""
    doc = Document(
        document_id="doc_reindex_json_505",
        filename="reindex_overwrite.pdf",
        page_count=1,
        chunk_count=0,
        status="indexing_required",
        version=1,
        is_active=False,
    )
    db_session.add(doc)
    db_session.commit()

    mock_pages = (1, [(1, "Updated text after reindex")])
    mock_embeddings = [[0.5] * 768]

    with patch("backend.app.services.documents.download_file_from_storage", return_value=b"%PDF-reindex"), \
         patch("backend.app.services.documents.extract_document_pages", return_value=mock_pages), \
         patch("backend.app.services.documents.generate_embeddings", return_value=mock_embeddings), \
         patch("backend.app.services.vector_store.upload_file_to_storage") as mock_upload, \
         patch("backend.app.services.vector_store.get_collection"):

        res = reindex_document("doc_reindex_json_505", db_session)
        assert res["status"] == "processed"
        assert res["chunk_count"] == 1

        mock_upload.assert_called_once()
        call_args = mock_upload.call_args
        object_key = call_args[1]["object_key"] if "object_key" in call_args[1] else call_args[0][1]
        assert object_key == "vectors/doc_reindex_json_505.json"


def test_real_embedding_array_serialization_precision():
    """TEST G: Verifies full numerical precision and dimension matching during real embedding serialization."""
    import json
    import numpy as np

    fake_embedding = np.random.rand(768).astype(np.float64)
    chunks = [{"text": "Sample text", "metadata": {"document_id": "precision_doc", "page": 1, "chunk_index": 0}}]

    with patch("backend.app.services.vector_store.get_collection"), \
         patch("backend.app.services.vector_store.upload_file_to_storage") as mock_upload:

        from backend.app.services.vector_store import store_chunks
        store_chunks(chunks, [fake_embedding.tolist()])

        call_args = mock_upload.call_args
        content = call_args[1]["content"] if "content" in call_args[1] else call_args[0][0]
        payload = json.loads(content.decode("utf-8"))

        restored_vector = payload["embeddings"][0]
        assert len(restored_vector) == 768
        assert abs(restored_vector[0] - fake_embedding[0]) < 1e-7


def test_stalled_self_healing_lock_expires_allowing_manual_reindex(db_session: Session):
    """Change #4A Test 1 & 3: Stalled/expired lock does not permanently block manual admin re-index."""
    import time
    from backend.app.services.documents import _REINDEXING_IN_PROGRESS, _REINDEX_LOCK, reindex_document

    doc_id = "doc_stalled_lock_606"
    doc = Document(
        document_id=doc_id,
        filename="stalled_lock_sample.pdf",
        page_count=1,
        chunk_count=0,
        status="indexing_required",
        version=1,
        is_active=False,
    )
    db_session.add(doc)
    db_session.commit()

    # Simulate a lock acquired 200 seconds ago (expired)
    with _REINDEX_LOCK:
        _REINDEXING_IN_PROGRESS[doc_id] = time.time() - 200.0

    mock_pages = (1, [(1, "Text extracted after lock expiration")])
    mock_embeddings = [[0.3] * 768]

    with patch("backend.app.services.documents.download_file_from_storage", return_value=b"%PDF-sample"), \
         patch("backend.app.services.documents.extract_document_pages", return_value=mock_pages), \
         patch("backend.app.services.documents.generate_embeddings", return_value=mock_embeddings), \
         patch("backend.app.services.vector_store.upload_file_to_storage"), \
         patch("backend.app.services.vector_store.get_collection"):

        res = reindex_document(doc_id, db_session)
        assert res["status"] == "processed"
        assert res["chunk_count"] == 1


def test_fresh_active_lock_prevents_concurrent_reindexing():
    """Change #4A Test 2: Active fresh lock (< 120s) rejects concurrent reindex attempts."""
    import time
    from backend.app.services.documents import (
        _REINDEXING_IN_PROGRESS,
        _REINDEX_LOCK,
        acquire_reindex_lock,
        release_reindex_lock,
    )

    doc_id = "doc_active_lock_707"
    with _REINDEX_LOCK:
        _REINDEXING_IN_PROGRESS[doc_id] = time.time()  # Fresh lock just acquired

    try:
        assert acquire_reindex_lock(doc_id) is False
    finally:
        release_reindex_lock(doc_id)
