import os
import pytest
from backend.app.models.user import User
from backend.app.services.admin_bootstrap import run_admin_bootstrap
from backend.app.services.auth import hash_password, verify_password


def test_admin_bootstrap_creates_admin_when_enabled(db_session, monkeypatch):
    monkeypatch.setenv("ADMIN_BOOTSTRAP_ENABLED", "true")
    monkeypatch.setenv("ADMIN_EMAIL", "testadmin@gcet.edu.in")
    monkeypatch.setenv("ADMIN_PASSWORD", "SuperSecurePassword123!")

    result = run_admin_bootstrap(db=db_session)
    assert result is True

    created_admin = (
        db_session.query(User)
        .filter(User.email == "testadmin@gcet.edu.in")
        .first()
    )
    assert created_admin is not None
    assert created_admin.role == "admin"
    assert created_admin.name == "GCET Administrator"
    assert verify_password("SuperSecurePassword123!", created_admin.password_hash)


def test_admin_bootstrap_does_not_duplicate_existing_admin(db_session, monkeypatch):
    existing_admin = User(
        name="Existing Admin",
        email="admin@gcet.edu.in",
        password_hash=hash_password("OriginalPassword123"),
        role="admin",
    )
    db_session.add(existing_admin)
    db_session.commit()

    monkeypatch.setenv("ADMIN_BOOTSTRAP_ENABLED", "true")
    monkeypatch.setenv("ADMIN_EMAIL", "admin@gcet.edu.in")
    monkeypatch.setenv("ADMIN_PASSWORD", "NewDifferentPassword456")

    result = run_admin_bootstrap(db=db_session)
    assert result is False

    admin_count = (
        db_session.query(User)
        .filter(User.email == "admin@gcet.edu.in")
        .count()
    )
    assert admin_count == 1

    current_admin = (
        db_session.query(User)
        .filter(User.email == "admin@gcet.edu.in")
        .first()
    )
    assert verify_password("OriginalPassword123", current_admin.password_hash)
    assert not verify_password("NewDifferentPassword456", current_admin.password_hash)


def test_admin_bootstrap_does_not_promote_existing_student(db_session, monkeypatch):
    existing_student = User(
        name="Student User",
        email="student@gcet.edu.in",
        password_hash=hash_password("StudentPassword123"),
        role="student",
    )
    db_session.add(existing_student)
    db_session.commit()

    monkeypatch.setenv("ADMIN_BOOTSTRAP_ENABLED", "true")
    monkeypatch.setenv("ADMIN_EMAIL", "student@gcet.edu.in")
    monkeypatch.setenv("ADMIN_PASSWORD", "AttemptedAdminPassword")

    result = run_admin_bootstrap(db=db_session)
    assert result is False

    current_user = (
        db_session.query(User)
        .filter(User.email == "student@gcet.edu.in")
        .first()
    )
    assert current_user.role == "student"
    assert verify_password("StudentPassword123", current_user.password_hash)


def test_admin_bootstrap_other_student_records_remain_unchanged(db_session, monkeypatch):
    student_a = User(
        name="Student A",
        email="studenta@gcet.edu.in",
        password_hash=hash_password("PassA"),
        role="student",
    )
    student_b = User(
        name="Student B",
        email="studentb@gcet.edu.in",
        password_hash=hash_password("PassB"),
        role="student",
    )
    db_session.add_all([student_a, student_b])
    db_session.commit()

    monkeypatch.setenv("ADMIN_BOOTSTRAP_ENABLED", "true")
    monkeypatch.setenv("ADMIN_EMAIL", "brandnewadmin@gcet.edu.in")
    monkeypatch.setenv("ADMIN_PASSWORD", "BrandNewPass123")

    result = run_admin_bootstrap(db=db_session)
    assert result is True

    re_a = db_session.query(User).filter(User.email == "studenta@gcet.edu.in").first()
    re_b = db_session.query(User).filter(User.email == "studentb@gcet.edu.in").first()

    assert re_a.role == "student"
    assert verify_password("PassA", re_a.password_hash)
    assert re_b.role == "student"
    assert verify_password("PassB", re_b.password_hash)


def test_admin_bootstrap_disabled_does_nothing(db_session, monkeypatch):
    monkeypatch.setenv("ADMIN_BOOTSTRAP_ENABLED", "false")
    monkeypatch.setenv("ADMIN_EMAIL", "newadmin@gcet.edu.in")
    monkeypatch.setenv("ADMIN_PASSWORD", "Password123")

    result = run_admin_bootstrap(db=db_session)
    assert result is False

    user = db_session.query(User).filter(User.email == "newadmin@gcet.edu.in").first()
    assert user is None
