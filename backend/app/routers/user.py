from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.user import User
from backend.app.schemas.user import (
    UserResponse,
    UpdateUserRequest,
    ChangePasswordRequest,
)
from backend.app.services.user import (
    get_current_profile,
    update_profile,
    change_password,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# --------------------------------------------------------
# Get Current User
# --------------------------------------------------------
@router.get(
    "/me",
    response_model=UserResponse,
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return get_current_profile(current_user)


# --------------------------------------------------------
# Update Profile
# --------------------------------------------------------
@router.patch(
    "/me",
    response_model=UserResponse,
)
def update_my_profile(
    data: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return update_profile(
        data,
        current_user,
        db,
    )


# --------------------------------------------------------
# Change Password
# --------------------------------------------------------
@router.patch(
    "/change-password",
)
def update_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return change_password(
        data,
        current_user,
        db,
    )