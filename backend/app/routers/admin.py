from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.roles import UserRole
from backend.app.core.security import require_admin
from backend.app.core.sorting import UserSort
from backend.app.models.user import User
from backend.app.schemas.admin import (
    AdminUserResponse,
    PaginatedUsersResponse,
    UpdateUserRoleRequest,
)
from backend.app.services.admin import (
    get_all_users,
    update_user_role,
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


# --------------------------------------------------------
# Get All Users
# --------------------------------------------------------
@router.get(
    "/users",
    response_model=PaginatedUsersResponse,
)
def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = None,
    role: UserRole | None = None,
    sort: UserSort = UserSort.NEWEST,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return get_all_users(
        db=db,
        page=page,
        limit=limit,
        search=search,
        role=role,
        sort=sort,
    )


# --------------------------------------------------------
# Update User Role
# --------------------------------------------------------
@router.patch(
    "/users/{user_id}/role",
    response_model=AdminUserResponse,
)
def change_user_role(
    user_id: int,
    request: UpdateUserRoleRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return update_user_role(
        user_id=user_id,
        role=request.role,
        db=db,
    )