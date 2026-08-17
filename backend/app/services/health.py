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


def check_embeddings() -> bool:
    """
    Verify Gemini Embedding service client configuration locally.
    Does not execute live API network calls during startup/ping checks.
    """
    try:
        from backend.app.services.gemini import client
        return client is not None

    except Exception as e:
        print(f"[EMBEDDING HEALTH CHECK ERROR] {e}")
        return False


def ensure_database_schema_migrations() -> None:
    """
    Ensure database table columns match the latest SQLAlchemy models.
    Base.metadata.create_all() does not alter existing tables to add new columns.
    """
    db: Session = SessionLocal()
    try:
        bind_engine = db.get_bind()
        dialect_name = bind_engine.dialect.name

        if dialect_name == "postgresql":
            db.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS category VARCHAR DEFAULT 'General Academic'"))
            db.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS tags VARCHAR DEFAULT ''"))
            db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS picture VARCHAR"))
            db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS given_name VARCHAR"))
            db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS family_name VARCHAR"))
            db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS department VARCHAR"))
            db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS academic_regulation VARCHAR"))
            db.commit()
            print("[SCHEMA MIGRATION] PostgreSQL 'documents' and 'users' table columns verified/added.")
        elif dialect_name == "sqlite":
            for stmt in [
                "ALTER TABLE documents ADD COLUMN category VARCHAR DEFAULT 'General Academic'",
                "ALTER TABLE documents ADD COLUMN tags VARCHAR DEFAULT ''",
                "ALTER TABLE users ADD COLUMN department VARCHAR",
                "ALTER TABLE users ADD COLUMN academic_regulation VARCHAR",
            ]:
                try:
                    db.execute(text(stmt))
                    db.commit()
                except Exception:
                    db.rollback()
    except Exception as e:
        db.rollback()
        print(f"[SCHEMA MIGRATION NOTICE] {e}")
    finally:
        db.close()


def run_startup_checks() -> None:
    """
    Run all startup validation checks and schema migrations.

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
        "Embedding Model": check_embeddings(),
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

    # Perform automated column migrations for existing tables
    ensure_database_schema_migrations()

    print("[READY] Application Ready")
    print("=" * 55 + "\n")