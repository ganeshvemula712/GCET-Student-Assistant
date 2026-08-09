from unittest.mock import patch


def test_chat_api_success(client):

    with patch(
        "backend.app.routers.chat.process_chat"
    ) as mock_chat:

        mock_chat.return_value = {
            "answer": "Hello Student",
            "sources": [],
        }

        response = client.post(
            "/chat",
            json={
                "conversation_id": "conv-123",
                "question": "Hello"
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == "Hello Student"
    assert data["sources"] == []


def test_chat_api_validation(client):

    response = client.post(
        "/chat",
        json={
            "conversation_id": "conv-123"
        },
    )

    assert response.status_code == 422


def test_chat_api_empty_body(client):

    response = client.post(
        "/chat",
        json={},
    )

    assert response.status_code == 422