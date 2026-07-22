from fastapi import APIRouter, Depends

from backend.app.core.security import (
    get_current_user,
)
from backend.app.models.user import User

from backend.app.services.health import (
    check_database,
    check_chromadb,
    check_gemini,
)

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
def health_check(
    current_user: User = Depends(
        get_current_user,
    ),
):

    database = check_database()
    chromadb = check_chromadb()
    gemini = check_gemini()

    overall = all(
        [
            database,
            chromadb,
            gemini,
        ]
    )

    return {
        "status": "healthy" if overall else "unhealthy",
        "services": {
            "database": database,
            "chromadb": chromadb,
            "gemini": gemini,
        },
        "version": "1.0.0",
    }