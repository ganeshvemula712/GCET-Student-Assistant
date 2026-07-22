import pytest

from fastapi.testclient import TestClient

from backend.main import app

from backend.app.core.database import (
    Base,
    get_db,
)

from backend.app.core.security import (
    get_current_user,
    require_admin,
)

from tests.test_database import (
    engine,
    TestingSessionLocal,
)

from tests.fixtures.database import (
    create_student,
    create_admin,
    create_conversation,
)


# -------------------------------------------------------
# Fresh Test Database
# -------------------------------------------------------

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


# -------------------------------------------------------
# Database Override
# -------------------------------------------------------

def override_get_db():

    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# -------------------------------------------------------
# Database Fixture
# -------------------------------------------------------

@pytest.fixture
def db_session():

    db = TestingSessionLocal()

    try:
        yield db

    finally:

        db.rollback()

        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())

        db.commit()

        db.close()


# -------------------------------------------------------
# User Fixtures
# -------------------------------------------------------

@pytest.fixture
def student(db_session):

    return create_student(db_session)


@pytest.fixture
def admin(db_session):

    return create_admin(db_session)


@pytest.fixture
def conversation(
    db_session,
    student,
):

    return create_conversation(
        db_session,
        student,
    )


# -------------------------------------------------------
# Auth Overrides
# -------------------------------------------------------

@pytest.fixture
def client(student):

    def override_current_user():

        return student

    app.dependency_overrides[
        get_current_user
    ] = override_current_user

    return TestClient(app)


@pytest.fixture
def admin_client(admin):

    def override_admin():

        return admin

    app.dependency_overrides[
        require_admin
    ] = override_admin

    return TestClient(app)