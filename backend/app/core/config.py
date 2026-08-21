import os

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class Settings:
    """
    Application configuration.
    """

    APP_NAME: str = "GCET Student Assistant"

    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_API_KEY_SECONDARY: str = os.getenv("GEMINI_API_KEY_SECONDARY", "")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "")

    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    REFRESH_TOKEN_EXPIRE_DAYS: int = int(
        os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
    )

    STORAGE_PROVIDER: str = os.getenv("STORAGE_PROVIDER", "supabase")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SECRET_KEY: str = os.getenv("SUPABASE_SECRET_KEY", "")
    SUPABASE_STORAGE_BUCKET: str = os.getenv("SUPABASE_STORAGE_BUCKET", "gcet-documents")
    OCR_BATCH_SIZE: int = int(os.getenv("OCR_BATCH_SIZE", "4"))
    GEMINI_OCR_MODEL: str = os.getenv("GEMINI_OCR_MODEL", "gemini-2.5-flash")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    SELF_HEALING_INTERVAL_MINUTES: int = int(os.getenv("SELF_HEALING_INTERVAL_MINUTES", "60"))

    # Legacy R2 settings preserved for backward compatibility
    R2_ACCOUNT_ID: str = os.getenv("R2_ACCOUNT_ID", "")
    R2_ACCESS_KEY_ID: str = os.getenv("R2_ACCESS_KEY_ID", "")
    R2_SECRET_ACCESS_KEY: str = os.getenv("R2_SECRET_ACCESS_KEY", "")
    R2_BUCKET_NAME: str = os.getenv("R2_BUCKET_NAME", "gcet-student-assistant-docs")
    R2_ENDPOINT_URL: str = os.getenv("R2_ENDPOINT_URL", "")


settings = Settings()

# Backward compatibility
APP_NAME = settings.APP_NAME
DATABASE_URL = settings.DATABASE_URL
GEMINI_API_KEY = settings.GEMINI_API_KEY
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
STORAGE_PROVIDER = settings.STORAGE_PROVIDER
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_SECRET_KEY = settings.SUPABASE_SECRET_KEY
SUPABASE_STORAGE_BUCKET = settings.SUPABASE_STORAGE_BUCKET
OCR_BATCH_SIZE = settings.OCR_BATCH_SIZE
GEMINI_OCR_MODEL = settings.GEMINI_OCR_MODEL
SELF_HEALING_INTERVAL_MINUTES = settings.SELF_HEALING_INTERVAL_MINUTES
R2_ACCOUNT_ID = settings.R2_ACCOUNT_ID
R2_ACCESS_KEY_ID = settings.R2_ACCESS_KEY_ID
R2_SECRET_ACCESS_KEY = settings.R2_SECRET_ACCESS_KEY
R2_BUCKET_NAME = settings.R2_BUCKET_NAME
R2_ENDPOINT_URL = settings.R2_ENDPOINT_URL