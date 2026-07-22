from fastapi.testclient import TestClient

from backend.main import app
from backend.app.core.security import get_current_user


class FakeUser:
    id = 1
    email = "admin@gmail.com"
    role = "admin"


def override_user():
    return FakeUser()


app.dependency_overrides[get_current_user] = override_user

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    body = response.json()

    assert "status" in body
    assert "services" in body
    assert "version" in body