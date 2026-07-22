from fastapi import HTTPException
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from backend.app.core.pagination import paginate
from backend.app.core.roles import UserRole
from backend.app.core.sorting import UserSort
from backend.app.models.user import User


# --------------------------------------------------------
# Get All Users
# --------------------------------------------------------
def get_all_users(
    db: Session,
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
    role: UserRole | None = None,
    sort: UserSort = UserSort.NEWEST,
):
    """
    Return paginated users.
    """

    query = db.query(User)

    # ------------------------
    # Search
    # ------------------------
    if search:
        query = query.filter(
            User.name.ilike(f"%{search}%")
        )

    # ------------------------
    # Filter by role
    # ------------------------
    if role:
        query = query.filter(
            User.role == role.value
        )

    # ------------------------
    # Sorting
    # ------------------------
    if sort == UserSort.NEWEST:
        query = query.order_by(
            desc(User.created_at)
        )

    elif sort == UserSort.OLDEST:
        query = query.order_by(
            asc(User.created_at)
        )

    elif sort == UserSort.NAME_ASC:
        query = query.order_by(
            asc(User.name)
        )

    elif sort == UserSort.NAME_DESC:
        query = query.order_by(
            desc(User.name)
        )

    return paginate(
        query=query,
        page=page,
        limit=limit,
    )


# --------------------------------------------------------
# Update User Role
# --------------------------------------------------------
def update_user_role(
    user_id: int,
    role: UserRole,
    db: Session,
):
    """
    Update a user's role.
    """

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    if (
        user.role == UserRole.ADMIN
        and role == UserRole.STUDENT
    ):
        admin_count = (
            db.query(User)
            .filter(User.role == UserRole.ADMIN)
            .count()
        )

        if admin_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot remove the last administrator.",
            )

    user.role = role.value

    db.commit()
    db.refresh(user)

    return user