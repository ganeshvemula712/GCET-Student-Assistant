from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.schemas.user import (
    UpdateUserRequest,
    ChangePasswordRequest,
)
from backend.app.services.auth import (
    hash_password,
    verify_password,
)


# --------------------------------------------------------
# Get Current User Profile
# --------------------------------------------------------
def get_current_profile(
    current_user: User,
):
    return current_user


# --------------------------------------------------------
# Update User Profile
# --------------------------------------------------------
def update_profile(
    data: UpdateUserRequest,
    current_user: User,
    db: Session,
):

    current_user.name = data.name

    db.commit()
    db.refresh(current_user)

    return current_user


# --------------------------------------------------------
# Change Password
# --------------------------------------------------------
def change_password(
    data: ChangePasswordRequest,
    current_user: User,
    db: Session,
):

    if not verify_password(
        data.current_password,
        current_user.password_hash,
    ):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect.",
        )

    current_user.password_hash = hash_password(
        data.new_password
    )

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Password changed successfully."
    }