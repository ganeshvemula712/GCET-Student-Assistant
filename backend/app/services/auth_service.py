from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.core.exceptions import UserAlreadyExistsException
from backend.app.models.user import User
from backend.app.schemas.user import (
    UserLogin,
    UserRegister,
)
from backend.app.services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_access_token,
)


def register_user(
    user: UserRegister,
    db: Session,
) -> User:
    """
    Register a new user.
    """

    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise UserAlreadyExistsException()

    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=hash_password(
            user.password
        ),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def login_user(
    user_login: UserLogin,
    db: Session,
) -> dict:
    """
    Authenticate a user and return JWT tokens.
    """

    user = (
        db.query(User)
        .filter(User.email == user_login.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    if not verify_password(
        user_login.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(
        {
            "sub": user.email,
        }
    )

    refresh_token = create_refresh_token(
        user.email
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


def refresh_access_token(
    refresh_token: str,
) -> dict:
    """
    Validate refresh token and generate a new access token.
    """

    try:
        payload = decode_access_token(
            refresh_token
        )

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token.",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token.",
        )

    email = payload.get("sub")

    if not email:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token.",
        )

    new_access_token = create_access_token(
        {
            "sub": email,
        }
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }