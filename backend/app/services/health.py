from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.services.gemini import client
from backend.app.services.vector_store import collection


def check_database() -> bool:
    """
    Check PostgreSQL connectivity.
    """
    db: Session = SessionLocal()

    try:
        db.execute(text("SELECT 1"))
        return True

    except Exception:
        return False

    finally:
        db.close()


def check_chromadb() -> bool:
    """
    Check ChromaDB connectivity.
    """
    try:
        collection.count()
        return True

    except Exception:
        return False


def check_gemini() -> bool:
    """
    Check Gemini client availability.
    """
    try:
        return client is not None

    except Exception:
        return False


def run_startup_checks() -> None:
    """
    Run all startup validation checks.

    Raises:
        RuntimeError: If any required service is unavailable.
    """

    print("\n" + "=" * 55)
    print("[START] Starting GCET Student Assistant Service")
    print("=" * 55)

    checks = {
        "Database": check_database(),
        "ChromaDB": check_chromadb(),
        "Gemini": check_gemini(),
    }

    failed = False

    for service, status in checks.items():
        if status:
            print(f"[OK] {service} Connected")
        else:
            print(f"[FAIL] {service} Connection Failed")
            failed = True

    print("=" * 55)

    if failed:
        raise RuntimeError(
            "Startup validation failed. One or more services are unavailable."
        )

    print("[READY] Application Ready")
    print("=" * 55 + "\n")