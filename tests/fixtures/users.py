from backend.app.models.user import User


def create_student_user():

    return User(
        id=1,
        name="Test Student",
        email="student@test.com",
        password_hash="hashed-password",
        role="student",
    )


def create_admin_user():

    return User(
        id=2,
        name="Test Admin",
        email="admin@test.com",
        password_hash="hashed-password",
        role="admin",
    )