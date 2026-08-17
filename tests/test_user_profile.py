import pytest
from backend.app.schemas.user import UpdateUserRequest
from backend.app.services.user import get_current_profile, update_profile

def test_get_current_profile_defaults(student):
    profile = get_current_profile(student)
    assert profile.id == student.id
    assert profile.email == student.email
    assert profile.name == student.name

def test_update_profile_department_and_regulation(db_session, student):
    data = UpdateUserRequest(
        name="Updated Student Name",
        department="CSE (AI & ML)",
        academic_regulation="R25 Academic Regulation"
    )
    updated_user = update_profile(data=data, current_user=student, db=db_session)
    assert updated_user.name == "Updated Student Name"
    assert updated_user.department == "CSE (AI & ML)"
    assert updated_user.academic_regulation == "R25 Academic Regulation"

def test_update_profile_partial(db_session, student):
    data = UpdateUserRequest(
        name="Only Name Change",
        department=None,
        academic_regulation=None
    )
    updated_user = update_profile(data=data, current_user=student, db=db_session)
    assert updated_user.name == "Only Name Change"
