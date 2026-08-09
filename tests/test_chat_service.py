from unittest.mock import patch

from backend.app.models.conversation import Conversation
from backend.app.services.chat import process_chat
from tests.fixtures.chat import (
    create_chat_request,
    create_duplicate_chunks,
    create_irrelevant_chunks,
    create_rag_chunks,
)


def test_process_chat_creates_new_conversation(
    db_session,
    student,
):

    request = create_chat_request()

    with patch(
        "backend.app.services.chat.generate_conversation_title"
    ) as mock_title, patch(
        "backend.app.services.chat.get_conversation_history"
    ) as mock_history, patch(
        "backend.app.services.chat.save_message"
    ) as mock_save_message, patch(
        "backend.app.services.chat.retrieve_relevant_chunks"
    ) as mock_retrieve, patch(
        "backend.app.services.chat.generate_general_answer"
    ) as mock_general:

        mock_title.return_value = "NBA Criterion 3"
        mock_history.return_value = ""
        mock_retrieve.return_value = []
        mock_general.return_value = ("General Answer", 80, [])

        response = process_chat(
            request=request,
            current_user=student,
            db=db_session,
        )

    conversation = (
        db_session.query(Conversation)
        .filter(
            Conversation.conversation_id
            == request.conversation_id
        )
        .first()
    )

    assert conversation is not None
    assert conversation.user_id == student.id
    assert conversation.title == "NBA Criterion 3"

    assert response.answer == "General Answer"
    assert response.sources == []

    assert mock_save_message.call_count == 2


def test_process_chat_reuses_existing_conversation(
    db_session,
    student,
):

    conversation = Conversation(
        conversation_id="conv-123",
        title="Existing Conversation",
        user_id=student.id,
    )

    db_session.add(conversation)
    db_session.commit()

    request = create_chat_request()

    with patch(
        "backend.app.services.chat.generate_conversation_title"
    ) as mock_title, patch(
        "backend.app.services.chat.get_conversation_history"
    ) as mock_history, patch(
        "backend.app.services.chat.save_message"
    ) as mock_save_message, patch(
        "backend.app.services.chat.retrieve_relevant_chunks"
    ) as mock_retrieve, patch(
        "backend.app.services.chat.generate_general_answer"
    ) as mock_general:

        mock_history.return_value = ""
        mock_retrieve.return_value = []
        mock_general.return_value = ("Existing Answer", 80, [])

        response = process_chat(
            request=request,
            current_user=student,
            db=db_session,
        )

    assert response.answer == "Existing Answer"

    mock_title.assert_not_called()

    assert mock_save_message.call_count == 2


def test_process_chat_generates_title_only_once(
    db_session,
    student,
):

    conversation = Conversation(
        conversation_id="conv-123",
        title="Already Generated",
        user_id=student.id,
    )

    db_session.add(conversation)
    db_session.commit()

    request = create_chat_request()

    with patch(
        "backend.app.services.chat.generate_conversation_title"
    ) as mock_title, patch(
        "backend.app.services.chat.get_conversation_history"
    ) as mock_history, patch(
        "backend.app.services.chat.save_message"
    ) as mock_save_message, patch(
        "backend.app.services.chat.retrieve_relevant_chunks"
    ) as mock_retrieve, patch(
        "backend.app.services.chat.generate_general_answer"
    ) as mock_general:

        mock_history.return_value = ""
        mock_retrieve.return_value = []
        mock_general.return_value = ("Answer", 80, [])

        process_chat(
            request=request,
            current_user=student,
            db=db_session,
        )

    mock_title.assert_not_called()

    assert mock_save_message.call_count == 2

def test_process_chat_general_ai_path(
    db_session,
    student,
):

    request = create_chat_request()

    with patch(
        "backend.app.services.chat.generate_conversation_title"
    ) as mock_title, patch(
        "backend.app.services.chat.get_conversation_history"
    ) as mock_history, patch(
        "backend.app.services.chat.save_message"
    ) as mock_save_message, patch(
        "backend.app.services.chat.retrieve_relevant_chunks"
    ) as mock_retrieve, patch(
        "backend.app.services.chat.generate_general_answer"
    ) as mock_general:

        mock_title.return_value = "General Chat"
        mock_history.return_value = "Previous Conversation"

        mock_retrieve.return_value = (
            create_irrelevant_chunks()
        )

        mock_general.return_value = (
            "This is a general AI answer.",
            80,
            [],
        )

        response = process_chat(
            request=request,
            current_user=student,
            db=db_session,
        )

    assert (
        response.answer
        == "This is a general AI answer."
    )

    assert response.sources == []

    mock_general.assert_called_once()

    assert mock_save_message.call_count == 2


def test_process_chat_rag_path(
    db_session,
    student,
):

    request = create_chat_request()

    with patch(
        "backend.app.services.chat.generate_conversation_title"
    ) as mock_title, patch(
        "backend.app.services.chat.get_conversation_history"
    ) as mock_history, patch(
        "backend.app.services.chat.save_message"
    ) as mock_save_message, patch(
        "backend.app.services.chat.retrieve_relevant_chunks"
    ) as mock_retrieve, patch(
        "backend.app.services.chat.generate_rag_answer"
    ) as mock_rag:

        mock_title.return_value = "NBA"

        mock_history.return_value = (
            "Previous Conversation"
        )

        mock_retrieve.return_value = (
            create_rag_chunks()
        )

        mock_rag.return_value = (
            "Outcome Based Education",
            85,
            [],
        )

        response = process_chat(
            request=request,
            current_user=student,
            db=db_session,
        )

    assert (
        response.answer
        == "Outcome Based Education"
    )

    assert len(response.sources) == 2

    assert (
        response.sources[0].filename
        == "NBA.pdf"
    )

    assert (
        response.sources[0].page
        == 15
    )

    assert (
        response.sources[1].page
        == 16
    )

    mock_rag.assert_called_once()

    assert mock_save_message.call_count == 2


def test_duplicate_sources_removed(
    db_session,
    student,
):

    request = create_chat_request()

    with patch(
        "backend.app.services.chat.generate_conversation_title"
    ) as mock_title, patch(
        "backend.app.services.chat.get_conversation_history"
    ) as mock_history, patch(
        "backend.app.services.chat.save_message"
    ) as mock_save_message, patch(
        "backend.app.services.chat.retrieve_relevant_chunks"
    ) as mock_retrieve, patch(
        "backend.app.services.chat.generate_rag_answer"
    ) as mock_rag:

        mock_title.return_value = "NBA"

        mock_history.return_value = ""

        mock_retrieve.return_value = (
            create_duplicate_chunks()
        )

        mock_rag.return_value = (
            "Duplicate Removed",
            85,
            [],
        )

        response = process_chat(
            request=request,
            current_user=student,
            db=db_session,
        )

    assert len(response.sources) == 1

    assert (
        response.sources[0].filename
        == "NBA.pdf"
    )

    assert (
        response.sources[0].page
        == 15
    )

    mock_save_message.assert_called()

def test_existing_conversation_belongs_to_current_user(
    db_session,
    student,
):

    conversation = Conversation(
        conversation_id="conv-123",
        title="Existing",
        user_id=student.id,
    )

    db_session.add(conversation)
    db_session.commit()

    request = create_chat_request()

    with patch(
        "backend.app.services.chat.generate_conversation_title"
    ) as mock_title, patch(
        "backend.app.services.chat.get_conversation_history"
    ) as mock_history, patch(
        "backend.app.services.chat.save_message"
    ) as mock_save_message, patch(
        "backend.app.services.chat.retrieve_relevant_chunks"
    ) as mock_retrieve, patch(
        "backend.app.services.chat.generate_general_answer"
    ) as mock_general:

        mock_history.return_value = ""
        mock_retrieve.return_value = []
        mock_general.return_value = ("Answer", 80, [])

        response = process_chat(
            request=request,
            current_user=student,
            db=db_session,
        )

    assert response.answer == "Answer"

    mock_title.assert_not_called()

    assert mock_save_message.call_count == 2

def test_title_generation_failure_does_not_stop_chat(
    db_session,
    student,
):

    request = create_chat_request()

    with patch(
        "backend.app.services.chat.generate_conversation_title"
    ) as mock_title, patch(
        "backend.app.services.chat.get_conversation_history"
    ) as mock_history, patch(
        "backend.app.services.chat.save_message"
    ) as mock_save_message, patch(
        "backend.app.services.chat.retrieve_relevant_chunks"
    ) as mock_retrieve, patch(
        "backend.app.services.chat.generate_general_answer"
    ) as mock_general:

        mock_title.side_effect = Exception(
            "Gemini unavailable"
        )

        mock_history.return_value = ""

        mock_retrieve.return_value = []

        mock_general.return_value = (
            "Fallback Answer",
            80,
            [],
        )

        response = process_chat(
            request=request,
            current_user=student,
            db=db_session,
        )

    conversation = (
        db_session.query(Conversation)
        .filter(
            Conversation.conversation_id
            == request.conversation_id
        )
        .first()
    )

    assert conversation is not None

    assert (
        conversation.title
        == "New Conversation"
    )

    assert (
        response.answer
        == "Fallback Answer"
    )

    assert mock_save_message.call_count == 2


def test_messages_are_saved(
    db_session,
    student,
):

    request = create_chat_request()

    with patch(
        "backend.app.services.chat.generate_conversation_title"
    ) as mock_title, patch(
        "backend.app.services.chat.get_conversation_history"
    ) as mock_history, patch(
        "backend.app.services.chat.retrieve_relevant_chunks"
    ) as mock_retrieve, patch(
        "backend.app.services.chat.generate_general_answer"
    ) as mock_general, patch(
        "backend.app.services.chat.save_message"
    ) as mock_save_message:

        mock_title.return_value = "Chat"

        mock_history.return_value = ""

        mock_retrieve.return_value = []

        mock_general.return_value = (
            "Assistant Reply",
            80,
            [],
        )

        process_chat(
            request=request,
            current_user=student,
            db=db_session,
        )

    assert mock_save_message.call_count == 2

    first_call = mock_save_message.call_args_list[0]
    second_call = mock_save_message.call_args_list[1]

    assert first_call.kwargs["role"] == "user"

    assert (
        first_call.kwargs["content"]
        == request.question
    )

    assert (
        second_call.kwargs["role"]
        == "assistant"
    )

    assert (
        second_call.kwargs["content"]
        == "Assistant Reply"
    )


def test_rag_returns_sorted_sources(
    db_session,
    student,
):

    request = create_chat_request()

    chunks = [
        {
            "text": "Chunk B",
            "distance": 0.30,
            "metadata": {
                "filename": "B.pdf",
                "page": 10,
            },
        },
        {
            "text": "Chunk A",
            "distance": 0.20,
            "metadata": {
                "filename": "A.pdf",
                "page": 5,
            },
        },
    ]

    with patch(
        "backend.app.services.chat.generate_conversation_title"
    ) as mock_title, patch(
        "backend.app.services.chat.get_conversation_history"
    ) as mock_history, patch(
        "backend.app.services.chat.save_message"
    ) as mock_save_message, patch(
        "backend.app.services.chat.retrieve_relevant_chunks"
    ) as mock_retrieve, patch(
        "backend.app.services.chat.generate_rag_answer"
    ) as mock_rag:

        mock_title.return_value = "Sorted"

        mock_history.return_value = ""

        mock_retrieve.return_value = chunks

        mock_rag.return_value = (
            "Sorted Response",
            85,
            [],
        )

        response = process_chat(
            request=request,
            current_user=student,
            db=db_session,
        )

    assert len(response.sources) == 2

    assert response.sources[0].filename == "A.pdf"
    assert response.sources[0].page == 5

    assert response.sources[1].filename == "B.pdf"
    assert response.sources[1].page == 10

    mock_rag.assert_called_once()
    assert mock_save_message.call_count == 2