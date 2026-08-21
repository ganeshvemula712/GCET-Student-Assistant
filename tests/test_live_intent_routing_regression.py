import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.schemas.chat import ChatRequest
from backend.app.services.intent import is_explicit_gcet_query, is_pure_general_concept, should_bypass_retrieval
from backend.app.services.chat_stream import stream_chat


# ----------------------------------------------------
# 1. Direct Intent Routing Matrix Tests
# ----------------------------------------------------

MUST_BYPASS_GENERAL_QUERIES = [
    "What is RAG?",
    "What is FastAPI?",
    "What is an API?",
    "Explain machine learning.",
    "What are embeddings?",
    "What is ChromaDB?",
    "What is a vector database?",
    "Write a Java program to reverse a string.",
    "How do I reverse an array in Java?",
    "How to reverse an array in Java?",
    "Reverse an array in Java.",
    "Explain how to reverse an array in Java.",
    "How do I sort an array in Java?",
    "Write a Python program to reverse a list.",
    "How do I reverse a string in Python?",
    "Explain binary search in Java.",
    "How do I implement a linked list in Java?",
    "What is a Java constructor?",
]

MUST_USE_RAG_GCET_QUERIES = [
    "What are the attendance requirements at GCET?",
    "What is the minimum attendance required for examinations at GCET?",
    "What are the placement eligibility criteria at GCET?",
    "What is the academic calendar at GCET?",
    "What is the I year CSE timetable?",
    "What is the IV year I sem timetable?",
    "What are the rules for mobile phones at GCET?",
    "What are the examination rules at GCET?",
    "What are the hostel rules at GCET?",
]

AMBIGUOUS_ACADEMIC_QUERIES = [
    "What is the attendance requirement?",
    "What are the placement rules?",
    "When are the exams?",
    "What is the timetable?",
    "What are the rules?",
]


@pytest.mark.parametrize("q", MUST_BYPASS_GENERAL_QUERIES)
def test_general_queries_must_bypass_retrieval(q):
    """General AI queries MUST bypass ChromaDB retrieval completely."""
    gcet = is_explicit_gcet_query(q)
    gen = is_pure_general_concept(q)
    bypass = should_bypass_retrieval(q, q)

    assert gcet is False, f"Query '{q}' was falsely classified as explicit GCET!"
    assert gen is True, f"Query '{q}' was not recognized as a pure general concept!"
    assert bypass is True, f"Query '{q}' failed should_bypass_retrieval!"


@pytest.mark.parametrize("q", MUST_USE_RAG_GCET_QUERIES)
def test_explicit_gcet_queries_must_use_rag(q):
    """Explicit GCET queries MUST route to GCET RAG."""
    gcet = is_explicit_gcet_query(q)
    bypass = should_bypass_retrieval(q, q)

    assert gcet is True, f"Query '{q}' failed explicit GCET detection!"
    assert bypass is False, f"Query '{q}' falsely bypassed retrieval!"


@pytest.mark.parametrize("q", AMBIGUOUS_ACADEMIC_QUERIES)
def test_ambiguous_academic_queries_must_use_rag(q):
    """Ambiguous academic queries MUST route to GCET RAG as safe default."""
    bypass = should_bypass_retrieval(q, q)
    assert bypass is False, f"Ambiguous academic query '{q}' falsely bypassed retrieval!"


# ----------------------------------------------------
# 2. Context Contamination Regression Tests
# ----------------------------------------------------

@pytest.mark.asyncio
async def test_previous_gcet_question_does_not_contaminate_subsequent_general_coding_question(db_session, student):
    """
    REGRESSION: Previous Q1 = 'What are the attendance requirements at GCET?'
    Then Q2 = 'How do I reverse an array in Java?'
    Q2 MUST route to General AI and NOT call ChromaDB!
    """
    request_obj = MagicMock()
    request_obj.is_disconnected = AsyncMock(return_value=False)

    # Simulated past conversation history with GCET question
    past_msg_gcet = "What are the attendance requirements at GCET?"

    with patch("backend.app.services.chat_stream.get_conversation_history", return_value=f"User: {past_msg_gcet}"), \
         patch("backend.app.services.chat_stream.save_message") as mock_save, \
         patch("backend.app.services.chat_stream.retrieve_relevant_chunks") as mock_retrieve, \
         patch("backend.app.services.chat_stream.generate_general_answer_stream") as mock_gen_stream:

        def dummy_gen(*args, **kwargs):
            yield "To reverse an array in Java..."

        mock_gen_stream.side_effect = dummy_gen
        mock_save.return_value = MagicMock(id="msg-999")

        events = []
        async for line in stream_chat(
            conversation_id="conv-cross-domain",
            question="How do I reverse an array in Java?",
            current_user=student,
            db=db_session,
            request=request_obj
        ):
            events.append(json.loads(line.strip()))

        # Vector retrieval MUST NOT be called for General AI coding question even in GCET conversation!
        mock_retrieve.assert_not_called()

        done_events = [e for e in events if e.get("type") == "done"]
        assert len(done_events) == 1
        data = done_events[0]

        assert data["mode"] == "general"
        assert data["is_rag"] is False
        assert data["sources"] == []


@pytest.mark.asyncio
async def test_previous_general_question_does_not_prevent_subsequent_gcet_rag_question(db_session, student):
    """
    REGRESSION: Previous Q1 = 'What is Java?'
    Then Q2 = 'What is the attendance requirement?'
    Q2 MUST route to GCET RAG!
    """
    request_obj = MagicMock()
    request_obj.is_disconnected = AsyncMock(return_value=False)

    past_msg_gen = "What is Java?"
    chunks = [
        {"text": "Attendance requirement is 75% aggregate.", "metadata": {"filename": "AR22.pdf", "page": 21}, "distance": 0.2}
    ]

    with patch("backend.app.services.chat_stream.get_conversation_history", return_value=f"User: {past_msg_gen}"), \
         patch("backend.app.services.chat_stream.save_message") as mock_save, \
         patch("backend.app.services.chat_stream.retrieve_relevant_chunks", return_value=chunks) as mock_retrieve, \
         patch("backend.app.services.chat_stream.generate_rag_answer_stream") as mock_rag_stream:

        def dummy_rag(*args, **kwargs):
            yield "Minimum aggregate attendance required is 75%."

        mock_rag_stream.side_effect = dummy_rag
        mock_save.return_value = MagicMock(id="msg-888")

        events = []
        async for line in stream_chat(
            conversation_id="conv-cross-domain-2",
            question="What is the attendance requirement?",
            current_user=student,
            db=db_session,
            request=request_obj
        ):
            events.append(json.loads(line.strip()))

        mock_retrieve.assert_called_once()

        done_events = [e for e in events if e.get("type") == "done"]
        assert len(done_events) == 1
        data = done_events[0]

        assert data["mode"] == "rag"
        assert data["is_rag"] is True
        assert len(data["sources"]) == 1
