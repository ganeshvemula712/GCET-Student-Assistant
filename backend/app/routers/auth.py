import os
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.rate_limiter import limiter
from backend.app.schemas.user import (
    GoogleAuthRequest,
    Token,
    RefreshTokenRequest,
    RefreshTokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from backend.app.services.auth_service import (
    authenticate_google_user,
    login_user,
    refresh_access_token,
    register_user,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# --------------------------------------------------------
# Register User
# --------------------------------------------------------
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
@limiter.limit("30/minute")
def register(
    request: Request,
    user: UserRegister,
    db: Session = Depends(get_db),
):
    user.email = user.email.strip().lower()
    return register_user(
        user=user,
        db=db,
    )


# --------------------------------------------------------
# Login User (Accepts JSON body {email, password}; exposes schema in Swagger UI)
# --------------------------------------------------------
@router.post(
    "/login",
    response_model=Token,
)
@limiter.limit("60/minute")
def login(
    request: Request,
    user_login: UserLogin,
    db: Session = Depends(get_db),
):
    user_login.email = user_login.email.strip().lower()

    tokens = login_user(
        user_login=user_login,
        db=db,
    )

    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": "bearer",
    }


# --------------------------------------------------------
# Google Auth Endpoint
# --------------------------------------------------------
@router.post(
    "/google",
    response_model=Token,
)
@limiter.limit("30/minute")
def google_auth(
    request: Request,
    body: GoogleAuthRequest,
    db: Session = Depends(get_db),
):
    return authenticate_google_user(
        body=body,
        db=db,
    )


# --------------------------------------------------------
# Google Auth URL Config Endpoint
# --------------------------------------------------------
@router.get("/google/url")
def get_google_auth_url():
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:5173/auth/google/callback")
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&redirect_uri={redirect_uri}&"
        f"response_type=code&scope=openid%20email%20profile"
    )
    return {
        "auth_url": auth_url,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "configured": bool(client_id),
    }


# --------------------------------------------------------
# Refresh Access Token
# --------------------------------------------------------
@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
)
@limiter.limit("60/minute")
def refresh_token(
    request: Request,
    body: RefreshTokenRequest,
):
    return refresh_access_token(
        body.refresh_token,
    )