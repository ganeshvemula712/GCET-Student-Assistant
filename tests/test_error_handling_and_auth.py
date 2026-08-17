import pytest
from backend.app.models.user import User
from backend.app.services.auth import hash_password
from backend.app.services.auth_service import login_user
from backend.app.schemas.user import UserLogin
from fastapi import HTTPException


def test_login_user_with_empty_password_hash(db_session):
    """Test that login for user with empty password_hash returns 401 instead of 500 crash."""
    user = User(
        name="Empty Hash Admin",
        email="emptyhash@gcet.edu.in",
        password_hash="",
        role="admin",
    )
    db_session.add(user)
    db_session.commit()

    login_schema = UserLogin(email="emptyhash@gcet.edu.in", password="anypassword")
    with pytest.raises(HTTPException) as exc_info:
        login_user(login_schema, db_session)

    assert exc_info.value.status_code == 401
    assert "Unable to sign in" in exc_info.value.detail


def test_login_user_with_malformed_password_hash(db_session):
    """Test that login for user with malformed password_hash returns 401 instead of 500 crash."""
    user = User(
        name="Malformed Hash User",
        email="malformed@gcet.edu.in",
        password_hash="invalid_bcrypt_or_argon_string_payload",
        role="student",
    )
    db_session.add(user)
    db_session.commit()

    login_schema = UserLogin(email="malformed@gcet.edu.in", password="anypassword")
    with pytest.raises(HTTPException) as exc_info:
        login_user(login_schema, db_session)

    assert exc_info.value.status_code == 401
    assert "Unable to sign in" in exc_info.value.detail


def test_login_user_with_valid_password(db_session):
    """Test that login with valid password succeeds cleanly."""
    valid_hash = hash_password("ValidPass123!")
    user = User(
        name="Valid User",
        email="valid@gcet.edu.in",
        password_hash=valid_hash,
        role="student",
    )
    db_session.add(user)
    db_session.commit()

    login_schema = UserLogin(email="valid@gcet.edu.in", password="ValidPass123!")
    res = login_user(login_schema, db_session)

    assert "access_token" in res
    assert "refresh_token" in res
    assert res["token_type"] == "bearer"
