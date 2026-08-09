from unittest.mock import patch

from backend.app.models.conversation import Conversation
from backend.app.models.message import Message


def test_conversation_detail_returns_message_ids(
    client,
    db_session,
    student,
):
    conversation = Conversation(
        conversation_id="detail-test-123",
        title="Detail Test",
        user_id=student.id,
    )

    db_session.add(conversation)
    db_session.commit()
    db_session.refresh(conversation)

    message = Message(
        conversation_id=conversation.conversation_id,
        role="user",
        content="Original question",
        sources=[],
    )

    db_session.add(message)
    db_session.commit()
    db_session.refresh(message)

    response = client.get("/conversations/detail-test-123")

    assert response.status_code == 200

    data = response.json()

    assert data["messages"][0]["id"] == message.id
    assert data["messages"][0]["content"] == "Original question"


def test_edit_message_route_calls_regeneration(
    client,
    db_session,
    student,
):
    conversation = Conversation(
        conversation_id="edit-test-123",
        title="Edit Test",
        user_id=student.id,
    )

    db_session.add(conversation)
    db_session.commit()
    db_session.refresh(conversation)

    message = Message(
        conversation_id=conversation.conversation_id,
        role="user",
        content="Original question",
        sources=[],
    )

    db_session.add(message)
    db_session.commit()
    db_session.refresh(message)

    with patch("backend.app.routers.messages.regenerate_message") as mock_regenerate:
        mock_regenerate.return_value = {"success": True}

        response = client.patch(
            f"/messages/{message.id}",
            json={"content": "Updated question"},
        )

    assert response.status_code == 200
    assert response.json()["message"] == "Message updated successfully"
    mock_regenerate.assert_called_once()


def test_rename_conversation(
    client,
    db_session,
    student,
):
    conversation = Conversation(
        conversation_id="rename-test-123",
        title="Old Title",
        user_id=student.id,
    )

    db_session.add(conversation)
    db_session.commit()
    db_session.refresh(conversation)

    response = client.patch(
        "/conversations/rename-test-123",
        json={
            "title": "New Title"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Conversation renamed successfully"
    assert data["conversation_id"] == "rename-test-123"
    assert data["title"] == "New Title"

    db_session.expire_all()
    
    updated = (
        db_session.query(Conversation)
        .filter(
            Conversation.conversation_id == "rename-test-123"
        )
        .first()
    )

    assert updated is not None
    assert updated.title == "New Title"


def test_search_conversations(
    client,
    db_session,
    student,
):
    conversation = Conversation(
        conversation_id="search-test-123",
        title="Attendance Questions",
        user_id=student.id,
    )

    db_session.add(conversation)
    db_session.commit()

    response = client.get(
        "/conversations/search?q=Attendance"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Attendance Questions"