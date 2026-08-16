import pytest
from unittest.mock import MagicMock, patch
from backend.app.services.storage import (
    get_storage_key,
    upload_file_to_storage,
    download_file_from_storage,
    delete_file_from_storage,
    check_object_exists,
)
from backend.app.services.startup import sync_chromadb_with_postgres

def test_get_storage_key_format():
    key = get_storage_key("abc123hash", "Test Document File.pdf")
    assert key == "documents/abc123hash/Test_Document_File.pdf"

def test_local_storage_fallback_lifecycle():
    test_key = "documents/test_hash_999/sample_test_doc.txt"
    sample_content = b"Hello GCET Assistant test content."

    # 1. Upload
    up_ok = upload_file_to_storage(sample_content, test_key, "text/plain")
    assert up_ok is True

    # 2. Check existence
    assert check_object_exists(test_key) is True

    # 3. Download
    downloaded = download_file_from_storage(test_key)
    assert downloaded == sample_content

    # 4. Delete
    del_ok = delete_file_from_storage(test_key)
    assert del_ok is True

    # 5. Verify deleted
    assert check_object_exists(test_key) is False

def test_production_mode_missing_credentials_fails_clearly(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    from backend.app.core import config
    monkeypatch.setattr(config.settings, "SUPABASE_URL", "")
    monkeypatch.setattr(config.settings, "SUPABASE_SECRET_KEY", "")

    # In production without credentials, upload must fail cleanly (return False) without fallback
    ok = upload_file_to_storage(b"test data", "documents/prod_test/test.txt")
    assert ok is False

def test_supabase_storage_mocked_lifecycle(monkeypatch):
    from backend.app.core import config
    monkeypatch.setattr(config.settings, "SUPABASE_URL", "https://mockproject.supabase.co")
    monkeypatch.setattr(config.settings, "SUPABASE_SECRET_KEY", "mock_secret_key_123")
    monkeypatch.setattr(config.settings, "SUPABASE_STORAGE_BUCKET", "gcet-documents")

    test_key = "documents/mock_hash_100/test_file.pdf"
    content = b"Mock PDF Content for Supabase Storage Test"

    # Mock httpx responses
    mock_post_res = MagicMock(status_code=200)
    mock_get_res = MagicMock(status_code=200, content=content)
    mock_del_res = MagicMock(status_code=200)

    with patch("httpx.Client") as mock_client_cls:
        client_instance = MagicMock()
        client_instance.post.return_value = mock_post_res
        client_instance.get.return_value = mock_get_res
        client_instance.delete.return_value = mock_del_res
        mock_client_cls.return_value.__enter__.return_value = client_instance

        # Test upload
        up_ok = upload_file_to_storage(content, test_key, "application/pdf")
        assert up_ok is True
        client_instance.post.assert_called_once()
        headers = client_instance.post.call_args.kwargs.get("headers", {})
        assert headers.get("Authorization") == "Bearer mock_secret_key_123"
        assert headers.get("apiKey") == "mock_secret_key_123"

        # Test download
        downloaded = download_file_from_storage(test_key)
        assert downloaded == content
        client_instance.get.assert_called_once()

        # Test existence check
        exists = check_object_exists(test_key)
        assert exists is True

        # Test delete
        del_ok = delete_file_from_storage(test_key)
        assert del_ok is True
        client_instance.delete.assert_called_once()

def test_self_healing_startup_sync_runs_without_error(db_session):
    # Running sync_chromadb_with_postgres should execute cleanly
    sync_chromadb_with_postgres()
