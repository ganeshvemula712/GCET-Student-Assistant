from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user

from backend.app.models.user import User

from backend.app.schemas.dashboard import (
    DashboardStatsResponse,
)

from backend.app.services.dashboard import (
    get_dashboard_stats,
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/stats",
    response_model=DashboardStatsResponse,
)
def dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_dashboard_stats(
        current_user=current_user,
        db=db,
    )