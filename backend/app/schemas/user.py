from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

class UserRegister(BaseModel):
    """
    Request schema for user registration.
    """

    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """
    Request schema for user login.
    """

    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    """
    Request schema for Google OAuth authentication.
    """

    credential: str | None = None
    email: EmailStr | None = None
    name: str | None = None


class UserResponse(BaseModel):
    """
    User details returned by the API.
    """

    id: int
    name: str
    email: EmailStr
    role: str
    department: str | None = None
    academic_regulation: str | None = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class UpdateUserRequest(BaseModel):
    """
    Request schema for updating user profile.
    """

    name: str
    department: str | None = None
    academic_regulation: str | None = None


class ChangePasswordRequest(BaseModel):
    """
    Request schema for changing password.
    """

    current_password: str
    new_password: str


class RefreshTokenRequest(BaseModel):
    """
    Request schema for refreshing an access token.
    """

    refresh_token: str


class Token(BaseModel):
    """
    Authentication token response.
    """

    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenResponse(BaseModel):
    """
    Response schema returned after refreshing an access token.
    """

    access_token: str
    token_type: str