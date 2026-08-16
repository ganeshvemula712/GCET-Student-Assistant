import pytest
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
    monkeypatch.setattr(config.settings, "R2_ACCESS_KEY_ID", "")
    monkeypatch.setattr(config.settings, "R2_SECRET_ACCESS_KEY", "")

    # In production without credentials, upload must fail cleanly (return False) without fallback
    ok = upload_file_to_storage(b"test data", "documents/prod_test/test.txt")
    assert ok is False

def test_self_healing_startup_sync_runs_without_error(db_session):
    # Running sync_chromadb_with_postgres should execute cleanly
    sync_chromadb_with_postgres()
