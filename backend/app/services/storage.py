import logging
import os
from io import BytesIO
import httpx

from backend.app.core.config import settings

logger = logging.getLogger("uvicorn")


def is_production_mode() -> bool:
    return bool(
        os.getenv("RENDER")
        or os.getenv("ENVIRONMENT") == "production"
        or settings.STORAGE_PROVIDER.lower() == "supabase"
    )


def is_supabase_configured() -> bool:
    return bool(settings.SUPABASE_URL and settings.SUPABASE_SECRET_KEY)


def get_storage_key(document_id: str, filename: str) -> str:
    clean_name = os.path.basename(filename).replace(" ", "_")
    return f"documents/{document_id}/{clean_name}"


def get_vector_storage_key(document_id: str) -> str:
    return f"vectors/{document_id}.json"


def _get_local_file_path(object_key: str) -> str:
    base_dir = os.path.abspath("documents_storage")
    safe_path = os.path.join(base_dir, object_key.replace("/", os.sep))
    os.makedirs(os.path.dirname(safe_path), exist_ok=True)
    return safe_path


def _get_supabase_headers(content_type: str | None = None) -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_SECRET_KEY}",
        "apiKey": settings.SUPABASE_SECRET_KEY,
    }
    if content_type:
        headers["Content-Type"] = content_type
    return headers


def upload_file_to_storage(
    content: bytes,
    object_key: str,
    content_type: str = "application/octet-stream",
) -> bool:
    if is_supabase_configured():
        try:
            url = f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/object/{settings.SUPABASE_STORAGE_BUCKET}/{object_key}"
            headers = _get_supabase_headers(content_type)
            headers["x-upsert"] = "true"
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, headers=headers, content=content)
                if response.status_code in (200, 201):
                    logger.info(f"[STORAGE] Uploaded '{object_key}' ({len(content)} bytes) to Supabase Storage.")
                    return True
                else:
                    logger.error(
                        f"[STORAGE ERROR] Failed uploading '{object_key}' to Supabase Storage. "
                        f"Status: {response.status_code}"
                    )
                    return False
        except Exception as err:
            logger.error(f"[STORAGE ERROR] Exception during Supabase upload for '{object_key}': {err}")
            return False
    else:
        if is_production_mode() and not os.getenv("PYTEST_CURRENT_TEST"):
            logger.error(
                f"[STORAGE ERROR] Cannot upload '{object_key}'. Supabase Storage is required in production, "
                "but SUPABASE_URL / SUPABASE_SECRET_KEY are missing."
            )
            return False
        # Fallback to local storage directory in development/testing mode
        try:
            local_path = _get_local_file_path(object_key)
            with open(local_path, "wb") as f:
                f.write(content)
            logger.info(f"[STORAGE] Saved '{object_key}' to local fallback storage: {local_path}")
            return True
        except Exception as err:
            logger.error(f"[STORAGE ERROR] Error writing '{object_key}' to local storage: {err}")
            return False


def download_file_from_storage(object_key: str) -> bytes | None:
    if is_supabase_configured():
        try:
            base = settings.SUPABASE_URL.rstrip('/')
            bucket = settings.SUPABASE_STORAGE_BUCKET
            headers = _get_supabase_headers()
            with httpx.Client(timeout=30.0) as client:
                # Try authenticated object endpoint
                auth_url = f"{base}/storage/v1/object/authenticated/{bucket}/{object_key}"
                res = client.get(auth_url, headers=headers)
                if res.status_code == 200:
                    logger.info(f"[STORAGE] Downloaded '{object_key}' ({len(res.content)} bytes) from Supabase Storage.")
                    return res.content

                # Fallback to standard object endpoint
                std_url = f"{base}/storage/v1/object/{bucket}/{object_key}"
                res2 = client.get(std_url, headers=headers)
                if res2.status_code == 200:
                    logger.info(f"[STORAGE] Downloaded '{object_key}' ({len(res2.content)} bytes) via standard object endpoint.")
                    return res2.content

                logger.warning(f"[STORAGE WARNING] Failed downloading '{object_key}' from Supabase. Status: {res.status_code}/{res2.status_code}")
                return None
        except Exception as err:
            logger.error(f"[STORAGE ERROR] Exception downloading '{object_key}' from Supabase: {err}")
            return None
    else:
        local_path = _get_local_file_path(object_key)
        if os.path.exists(local_path):
            with open(local_path, "rb") as f:
                return f.read()
        return None


def delete_file_from_storage(object_key: str) -> bool:
    if is_supabase_configured():
        try:
            base = settings.SUPABASE_URL.rstrip('/')
            bucket = settings.SUPABASE_STORAGE_BUCKET
            headers = _get_supabase_headers()
            with httpx.Client(timeout=30.0) as client:
                url = f"{base}/storage/v1/object/{bucket}/{object_key}"
                response = client.delete(url, headers=headers)
                if response.status_code in (200, 204):
                    logger.info(f"[STORAGE] Deleted '{object_key}' from Supabase Storage.")
                    return True
                else:
                    bulk_url = f"{base}/storage/v1/object/remove/{bucket}"
                    bulk_res = client.post(bulk_url, headers=headers, json={"prefixes": [object_key]})
                    if bulk_res.status_code == 200:
                        logger.info(f"[STORAGE] Deleted '{object_key}' via bulk remove from Supabase Storage.")
                        return True
                    logger.error(f"[STORAGE ERROR] Failed deleting '{object_key}' from Supabase. Status: {response.status_code}")
                    return False
        except Exception as err:
            logger.error(f"[STORAGE ERROR] Exception deleting '{object_key}' from Supabase: {err}")
            return False
    else:
        local_path = _get_local_file_path(object_key)
        if os.path.exists(local_path):
            try:
                os.remove(local_path)
                logger.info(f"[STORAGE] Deleted local fallback file: {local_path}")
                return True
            except Exception:
                return False
        return True


def check_object_exists(object_key: str) -> bool:
    if is_supabase_configured():
        try:
            base = settings.SUPABASE_URL.rstrip('/')
            bucket = settings.SUPABASE_STORAGE_BUCKET
            headers = _get_supabase_headers()
            with httpx.Client(timeout=10.0) as client:
                # Check info endpoint
                info_url = f"{base}/storage/v1/object/info/authenticated/{bucket}/{object_key}"
                res = client.get(info_url, headers=headers)
                if res.status_code == 200:
                    return True

                # Check list endpoint with prefix
                list_url = f"{base}/storage/v1/object/list/{bucket}"
                list_res = client.post(list_url, headers=headers, json={"prefix": object_key, "limit": 1})
                if list_res.status_code == 200:
                    data = list_res.json()
                    if isinstance(data, list) and len(data) > 0:
                        return True

                # Fallback range get
                get_url = f"{base}/storage/v1/object/authenticated/{bucket}/{object_key}"
                range_headers = {**headers, "Range": "bytes=0-0"}
                range_res = client.get(get_url, headers=range_headers)
                return range_res.status_code in (200, 206)
        except Exception:
            return False
    else:
        local_path = _get_local_file_path(object_key)
        return os.path.exists(local_path)
