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

    SECRET_KEY: str = os.getenv("SECRET_KEY", "")

    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    REFRESH_TOKEN_EXPIRE_DAYS: int = int(
        os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
    )

settings = Settings()

# Backward compatibility
APP_NAME = settings.APP_NAME
DATABASE_URL = settings.DATABASE_URL
GEMINI_API_KEY = settings.GEMINI_API_KEY
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS