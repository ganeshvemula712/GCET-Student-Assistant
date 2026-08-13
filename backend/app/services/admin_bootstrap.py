import logging
import os
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.models.user import User
from backend.app.services.auth import hash_password

logger = logging.getLogger("uvicorn")


def run_admin_bootstrap(db: Session = None) -> bool:
    """
    Temporary production Admin account creation bootstrap.
    Controlled strictly by environment variables:
      - ADMIN_BOOTSTRAP_ENABLED="true"
      - ADMIN_EMAIL
      - ADMIN_PASSWORD
    """
    enabled = os.getenv("ADMIN_BOOTSTRAP_ENABLED", "").strip().lower()
    if enabled not in ("true", "1", "yes"):
        return False

    admin_email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    admin_password = os.getenv("ADMIN_PASSWORD", "").strip()

    if not admin_email or not admin_password:
        logger.warning(
            "[ADMIN BOOTSTRAP] ADMIN_BOOTSTRAP_ENABLED is set, but ADMIN_EMAIL or ADMIN_PASSWORD is missing."
        )
        return False

    should_close_db = False
    if db is None:
        db = SessionLocal()
        should_close_db = True

    try:
        existing_user = (
            db.query(User)
            .filter(User.email.ilike(admin_email))
            .first()
        )

        if existing_user:
            if existing_user.role == "admin":
                logger.info(
                    f"[ADMIN BOOTSTRAP] Admin user '{admin_email}' already exists. Password unchanged."
                )
            else:
                logger.warning(
                    f"[ADMIN BOOTSTRAP] User '{admin_email}' already exists with non-admin role '{existing_user.role}'. "
                    "Skipping promotion to prevent accidental privilege escalation."
                )
            return False

        admin_user = User(
            name="GCET Administrator",
            email=admin_email,
            password_hash=hash_password(admin_password),
            role="admin",
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        logger.info(
            f"[ADMIN BOOTSTRAP] Successfully created Administrator account for '{admin_email}'."
        )
        return True

    except Exception as err:
        db.rollback()
        logger.error(
            f"[ADMIN BOOTSTRAP] Error during admin account creation: {err}"
        )
        return False
    finally:
        if should_close_db:
            db.close()
