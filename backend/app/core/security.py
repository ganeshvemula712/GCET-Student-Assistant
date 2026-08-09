from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.roles import UserRole
from backend.app.models.user import User
from backend.app.services.auth import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials.",
    )

    try:
        payload = decode_access_token(token)

        print("=" * 60)
        print("TOKEN")
        print(token)

        print("PAYLOAD")
        print(payload)

        email = payload.get("sub")

        if email is None:
            raise credentials_exception

        if payload.get("type") != "access":
            raise credentials_exception

    except Exception as e:
        print(e)
        raise credentials_exception

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if user is None:
        raise credentials_exception

    return user

# --------------------------------------------------------
# Role-Based Authorization
# --------------------------------------------------------
def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Allow only administrators.
    """

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required.",
        )

    return current_user


def require_student_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Allow students and administrators.
    """

    if current_user.role not in (
        UserRole.STUDENT,
        UserRole.ADMIN,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied.",
        )

    return current_user