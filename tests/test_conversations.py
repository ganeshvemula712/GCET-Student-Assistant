from backend.app.models.conversation import Conversation


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