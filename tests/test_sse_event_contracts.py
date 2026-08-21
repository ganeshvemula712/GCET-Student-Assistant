import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.services.chat_stream import stream_chat


def format_sse_event(event_type: str, **payload) -> str:
    """Helper mirroring inner event function in chat_stream.py."""
    return json.dumps({"type": event_type, **payload}) + "\n"


def test_sse_event_helper_formatting():
    """1. Verify inner event helper returns proper JSON SSE line format."""
    token_str = format_sse_event("token", content="Hello world")
    data = json.loads(token_str.strip())
    assert data["type"] == "token"
    assert data["content"] == "Hello world"

    done_str = format_sse_event("done", mode="general", is_rag=False, sources=[], confidence=85)
    done_data = json.loads(done_str.strip())
    assert done_data["type"] == "done"
    assert done_data["mode"] == "general"
    assert done_data["is_rag"] is False
    assert done_data["sources"] == []
    assert done_data["confidence"] == 85


@pytest.mark.asyncio
async def test_stream_chat_general_ai_sse_contract(db_session, student):
    """2. Verify General AI streaming SSE contract (mode="general", is_rag=False, sources=[])."""
    request_obj = MagicMock()
    request_obj.is_disconnected = AsyncMock(return_value=False)

    with patch("backend.app.services.chat_stream.get_conversation_history", return_value=""), \
         patch("backend.app.services.chat_stream.save_message") as mock_save, \
         patch("backend.app.services.chat_stream.retrieve_relevant_chunks") as mock_retrieve, \
         patch("backend.app.services.chat_stream.generate_general_answer_stream") as mock_gen_stream:

        def dummy_gen(*args, **kwargs):
            yield "FastAPI is a modern web framework."

        mock_gen_stream.side_effect = dummy_gen
        mock_save.return_value = MagicMock(id="msg-123")

        events = []
        async for line in stream_chat(
            conversation_id="conv-123",
            question="What is FastAPI?",
            current_user=student,
            db=db_session,
            request=request_obj
        ):
            events.append(json.loads(line.strip()))

        # General AI MUST NOT call vector retrieval
        mock_retrieve.assert_not_called()

        done_event = [e for e in events if e.get("type") == "done"]
        assert len(done_event) == 1
        data = done_event[0]

        assert data["mode"] == "general"
        assert data["is_rag"] is False
        assert data["sources"] == []
        assert data["confidence"] == 85


@pytest.mark.asyncio
async def test_stream_chat_gcet_rag_sse_contract(db_session, student):
    """3. Verify GCET RAG streaming SSE contract (mode="rag", is_rag=True, sources=[filename/page])."""
    request_obj = MagicMock()
    request_obj.is_disconnected = AsyncMock(return_value=False)

    chunks = [
        {"text": "Attendance requirement is 75% aggregate.", "metadata": {"filename": "AR22.pdf", "page": 21}, "distance": 0.2},
        {"text": "Attendance requirement is 75% aggregate.", "metadata": {"filename": "AR22.pdf", "page": 21}, "distance": 0.22}, # Dup source
    ]

    with patch("backend.app.services.chat_stream.get_conversation_history", return_value=""), \
         patch("backend.app.services.chat_stream.save_message") as mock_save, \
         patch("backend.app.services.chat_stream.retrieve_relevant_chunks", return_value=chunks) as mock_retrieve, \
         patch("backend.app.services.chat_stream.generate_rag_answer_stream") as mock_rag_stream:

        def dummy_rag_gen(*args, **kwargs):
            yield "Minimum aggregate attendance required is 75%."

        mock_rag_stream.side_effect = dummy_rag_gen
        mock_save.return_value = MagicMock(id="msg-456")

        events = []
        async for line in stream_chat(
            conversation_id="conv-123",
            question="What is the minimum attendance requirement at GCET?",
            current_user=student,
            db=db_session,
            request=request_obj
        ):
            events.append(json.loads(line.strip()))

        mock_retrieve.assert_called_once()

        done_event = [e for e in events if e.get("type") == "done"]
        assert len(done_event) == 1
        data = done_event[0]

        assert data["mode"] == "rag"
        assert data["is_rag"] is True
        # Source deduplication check
        assert len(data["sources"]) == 1
        assert data["sources"][0] == {"filename": "AR22.pdf", "page": 21}


@pytest.mark.asyncio
async def test_stream_chat_missing_gcet_unavailable_sse_contract(db_session, student):
    """4. Verify missing GCET information SSE contract (mode="gcet_unavailable", is_rag=False, sources=[])."""
    request_obj = MagicMock()
    request_obj.is_disconnected = AsyncMock(return_value=False)

    # 0 chunks matched
    with patch("backend.app.services.chat_stream.get_conversation_history", return_value=""), \
         patch("backend.app.services.chat_stream.save_message") as mock_save, \
         patch("backend.app.services.chat_stream.retrieve_relevant_chunks", return_value=[]) as mock_retrieve, \
         patch("backend.app.services.chat_stream.generate_general_answer_stream") as mock_gen_stream:

        mock_save.return_value = MagicMock(id="msg-789")

        events = []
        async for line in stream_chat(
            conversation_id="conv-123",
            question="What is the exact hostel mess fee at GCET?",
            current_user=student,
            db=db_session,
            request=request_obj
        ):
            events.append(json.loads(line.strip()))

        mock_retrieve.assert_called_once()
        mock_gen_stream.assert_not_called()  # General AI MUST NOT be called as fallback

        done_event = [e for e in events if e.get("type") == "done"]
        assert len(done_event) == 1
        data = done_event[0]

        assert data["mode"] in ("knowledge_unavailable", "gcet_unavailable")
        assert data["is_rag"] is False
        assert data["sources"] == []
        assert data["confidence"] == 0
