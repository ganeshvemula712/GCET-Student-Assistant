import logging
import os
from io import BytesIO

from backend.app.core.config import settings

logger = logging.getLogger("uvicorn")

_s3_client = None


def is_production_mode() -> bool:
    return bool(
        os.getenv("RENDER")
        or os.getenv("ENVIRONMENT") == "production"
        or settings.STORAGE_PROVIDER.lower() == "r2"
    )


def get_s3_client():
    global _s3_client
    if _s3_client is not None:
        return _s3_client

    if not settings.R2_ACCESS_KEY_ID or not settings.R2_SECRET_ACCESS_KEY:
        if is_production_mode() and not os.getenv("PYTEST_CURRENT_TEST"):
            logger.error(
                "[STORAGE ERROR] Cloudflare R2 credentials (R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY) "
                "are missing in production environment. Aborting S3 initialization."
            )
            return None
        logger.info("[STORAGE] R2 credentials not configured. Using local disk storage fallback for development.")
        return None

    try:
        import boto3
        from botocore.config import Config

        endpoint_url = settings.R2_ENDPOINT_URL
        if not endpoint_url and settings.R2_ACCOUNT_ID:
            endpoint_url = f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

        _s3_client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            config=Config(signature_version="s3v4"),
            region_name="auto",
        )
        logger.info(f"[STORAGE] Initialized S3 client for bucket '{settings.R2_BUCKET_NAME}'")
        return _s3_client
    except Exception as err:
        logger.error(f"[STORAGE] Failed to initialize S3 client: {err}")
        return None


def get_storage_key(document_id: str, filename: str) -> str:
    clean_name = os.path.basename(filename).replace(" ", "_")
    return f"documents/{document_id}/{clean_name}"


def _get_local_file_path(object_key: str) -> str:
    base_dir = os.path.abspath("documents_storage")
    safe_path = os.path.join(base_dir, object_key.replace("/", os.sep))
    os.makedirs(os.path.dirname(safe_path), exist_ok=True)
    return safe_path


def upload_file_to_storage(
    content: bytes,
    object_key: str,
    content_type: str = "application/octet-stream",
) -> bool:
    client = get_s3_client()
    if client:
        try:
            client.put_object(
                Bucket=settings.R2_BUCKET_NAME,
                Key=object_key,
                Body=content,
                ContentType=content_type,
            )
            logger.info(f"[STORAGE] Uploaded '{object_key}' ({len(content)} bytes) to Cloudflare R2.")
            return True
        except Exception as err:
            logger.error(f"[STORAGE] Error uploading '{object_key}' to R2: {err}")
            return False
    else:
        if is_production_mode() and not os.getenv("PYTEST_CURRENT_TEST"):
            logger.error(
                f"[STORAGE ERROR] Cannot upload '{object_key}'. R2 storage is required in production, "
                "but credentials are missing."
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
            logger.error(f"[STORAGE] Error writing '{object_key}' to local storage: {err}")
            return False


def download_file_from_storage(object_key: str) -> bytes | None:
    client = get_s3_client()
    if client:
        try:
            response = client.get_object(
                Bucket=settings.R2_BUCKET_NAME,
                Key=object_key,
            )
            data = response["Body"].read()
            logger.info(f"[STORAGE] Downloaded '{object_key}' ({len(data)} bytes) from R2.")
            return data
        except Exception as err:
            logger.warning(f"[STORAGE] Failed downloading '{object_key}' from R2: {err}")
            return None
    else:
        local_path = _get_local_file_path(object_key)
        if os.path.exists(local_path):
            with open(local_path, "rb") as f:
                return f.read()
        return None


def delete_file_from_storage(object_key: str) -> bool:
    client = get_s3_client()
    if client:
        try:
            client.delete_object(
                Bucket=settings.R2_BUCKET_NAME,
                Key=object_key,
            )
            logger.info(f"[STORAGE] Deleted '{object_key}' from R2.")
            return True
        except Exception as err:
            logger.error(f"[STORAGE] Error deleting '{object_key}' from R2: {err}")
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
    client = get_s3_client()
    if client:
        try:
            client.head_object(
                Bucket=settings.R2_BUCKET_NAME,
                Key=object_key,
            )
            return True
        except Exception:
            return False
    else:
        local_path = _get_local_file_path(object_key)
        return os.path.exists(local_path)
