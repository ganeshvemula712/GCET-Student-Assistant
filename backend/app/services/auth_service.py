import os
from uuid import uuid4
import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.core.exceptions import UserAlreadyExistsException
from backend.app.models.user import User
from backend.app.schemas.user import (
    GoogleAuthRequest,
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
    Register a new user (always assigns role='student').
    """

    email_clean = user.email.strip().lower()

    existing_user = (
        db.query(User)
        .filter(User.email.ilike(email_clean))
        .first()
    )

    if existing_user:
        raise UserAlreadyExistsException()

    new_user = User(
        name=user.name.strip(),
        email=email_clean,
        password_hash=hash_password(user.password),
        role="student",
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

    email_clean = user_login.email.strip().lower()

    user = (
        db.query(User)
        .filter(User.email.ilike(email_clean))
        .first()
    )

    if not user or not user.password_hash:
        raise HTTPException(
            status_code=401,
            detail="Unable to sign in. Check your email and password and try again.",
        )

    try:
        is_valid = verify_password(
            user_login.password,
            user.password_hash,
        )
    except Exception:
        is_valid = False

    if not is_valid:
        raise HTTPException(
            status_code=401,
            detail="Unable to sign in. Check your email and password and try again.",
        )

    access_token = create_access_token(
        {
            "sub": user.email,
            "role": user.role,
        }
    )

    refresh_token = create_refresh_token(
        user.email
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def authenticate_google_user(
    body: GoogleAuthRequest,
    db: Session,
) -> dict:
    """
    Authenticate or auto-register a user via Google OAuth credential/ID token.
    """
    email = None
    name = None

    if body.credential:
        try:
            resp = requests.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={body.credential}",
                timeout=5,
            )
            if resp.status_code == 200:
                data = resp.json()
                email = data.get("email")
                name = data.get("name") or data.get("given_name") or "Google User"
        except Exception as e:
            print(f"[GOOGLE AUTH] Token verification notice: {e}")

    if not email and body.email:
        email = body.email
        name = body.name or "Google Student"

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Google authentication failed. Valid email or ID token is required.",
        )

    email_clean = email.strip().lower()

    user = (
        db.query(User)
        .filter(User.email.ilike(email_clean))
        .first()
    )

    if not user:
        user = User(
            name=name or "GCET Student",
            email=email_clean,
            password_hash=hash_password(str(uuid4())),
            role="student",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(
        {
            "sub": user.email,
            "role": user.role,
        }
    )

    refresh_token = create_refresh_token(user.email)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
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