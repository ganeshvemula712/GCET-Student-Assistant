from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.rate_limiter import limiter
from backend.app.schemas.user import (
    Token,
    RefreshTokenRequest,
    RefreshTokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from backend.app.services.auth_service import (
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
@limiter.limit("3/minute")
def register(
    request: Request,
    user: UserRegister,
    db: Session = Depends(get_db),
):
    return register_user(
        user=user,
        db=db,
    )


# --------------------------------------------------------
# Login User
# --------------------------------------------------------
@router.post(
    "/login",
    response_model=Token,
)
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = UserLogin(
        email=form_data.username,
        password=form_data.password,
    )

    tokens = login_user(
        user_login=user,
        db=db,
    )

    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": "bearer",
    }


# --------------------------------------------------------
# Refresh Access Token
# --------------------------------------------------------
@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
)
@limiter.limit("10/minute")
def refresh_token(
    request: Request,
    body: RefreshTokenRequest,
):
    return refresh_access_token(
        body.refresh_token,
    )