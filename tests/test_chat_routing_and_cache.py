import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from backend.app.schemas.chat import ChatRequest
from backend.app.services.embeddings import generate_embeddings, generate_query_embedding, _cached_query_embedding
from backend.app.services.retrieval import RetrievalServiceError, retrieve_relevant_chunks
from backend.app.services.chat import process_chat
from backend.app.services.chat_stream import stream_chat
from tests.fixtures.chat import create_rag_chunks


def setup_function():
    # Clear query embedding cache before each test
    _cached_query_embedding.cache_clear()


async def _consume_stream(stream_gen):
    events = []
    async for item in stream_gen:
        events.append(item)
    return events


def test_query_embedding_cache_hit_and_miss():
    mock_vector = [0.1] * 3072
    mock_response = MagicMock()
    mock_response.embeddings = [MagicMock(values=mock_vector)]

    with patch("backend.app.services.embeddings.client.models.embed_content") as mock_embed:
        mock_embed.return_value = mock_response

        # 1. First call: Cache miss -> calls Gemini API
        vec1 = generate_query_embedding("What is the minimum attendance?")
        assert vec1 == mock_vector
        assert mock_embed.call_count == 1

        # 2. Identical query: Cache hit -> 0 extra API calls
        vec2 = generate_query_embedding("What is the minimum attendance?")
        assert vec2 == mock_vector
        assert mock_embed.call_count == 1

        # 3. Differently formatted equivalent query (extra spaces + uppercase): Cache hit -> 0 extra API calls
        vec3 = generate_query_embedding("  WHAT IS THE MINIMUM ATTENDANCE?  ")
        assert vec3 == mock_vector
        assert mock_embed.call_count == 1

        # 4. Different question: Cache miss -> calls Gemini API
        vec4 = generate_query_embedding("When are semester exams?")
        assert len(vec4) == 3072
        assert mock_embed.call_count == 2


def test_document_ingestion_does_not_use_query_cache():
    mock_vector = [0.5] * 3072
    mock_response = MagicMock()
    mock_response.embeddings = [MagicMock(values=mock_vector)]

    with patch("backend.app.services.embeddings.client.models.embed_content") as mock_embed:
        mock_embed.return_value = mock_response

        # Ingestion call directly to generate_embeddings
        res1 = generate_embeddings(["Chunk text 1"])
        assert len(res1) == 1
        assert mock_embed.call_count == 1

        # Duplicate ingestion call should NOT use LRU query cache (generate_embeddings does not cache)
        res2 = generate_embeddings(["Chunk text 1"])
        assert len(res2) == 1
        assert mock_embed.call_count == 2


@pytest.mark.parametrize("general_query", [
    "What is Python?",
    "Explain machine learning",
    "What is a neural network?",
    "Hello",
    "What is a package in Java?",
    "What is a batch in machine learning?",
    "What is a drive in computer systems?",
    "What is a company?",
    "What is a salary?",
    "What are regulations in general?"
])
def test_general_questions_bypass_or_fallback_to_general_knowledge(db_session, student, general_query):
    request = ChatRequest(conversation_id="conv-123", question=general_query)

    with patch("backend.app.services.chat.get_conversation_history") as mock_history, \
         patch("backend.app.services.chat.save_message") as mock_save_message, \
         patch("backend.app.services.chat.retrieve_relevant_chunks") as mock_retrieve, \
         patch("backend.app.services.chat.generate_general_answer") as mock_general:

        mock_history.return_value = ""
        mock_retrieve.return_value = [] # No GCET document chunks match generic technical query
        mock_general.return_value = ("General Knowledge Answer", 85, [])

        response = process_chat(request=request, current_user=student, db=db_session)

        assert response.answer == "General Knowledge Answer"


@pytest.mark.parametrize("gcet_query", [
    "What is the minimum attendance at GCET?",
    "What are GCET academic regulations?",
    "What is the syllabus for Data Science?",
    "When are IV year semester exams?",
    "Who got the highest salary among 2026 graduates?",
    "What was the highest package offered?",
    "Which company offered the highest package?",
    "Which companies visited GCET for placements?",
    "What are the placement statistics for 2026?",
    "What is the highest package at GCET?",
    "Which company offered the highest package to GCET students?",
    "What are the academic regulations at GCET?"
])
def test_gcet_questions_execute_retrieval(db_session, student, gcet_query):
    request = ChatRequest(conversation_id="conv-123", question=gcet_query)

    with patch("backend.app.services.chat.get_conversation_history") as mock_history, \
         patch("backend.app.services.chat.save_message") as mock_save_message, \
         patch("backend.app.services.chat.retrieve_relevant_chunks") as mock_retrieve, \
         patch("backend.app.services.chat.generate_rag_answer") as mock_rag:

        mock_history.return_value = ""
        mock_retrieve.return_value = create_rag_chunks()
        mock_rag.return_value = ("Grounded RAG Answer", 90, [])

        response = process_chat(request=request, current_user=student, db=db_session)

        assert response.answer == "Grounded RAG Answer"
        mock_retrieve.assert_called_once()


def test_strict_grounding_gcet_query_no_chunks_returns_kb_notice(db_session, student):
    request = ChatRequest(conversation_id="conv-123", question="Who got the highest salary among 2026 graduates?")

    with patch("backend.app.services.chat.get_conversation_history") as mock_history, \
         patch("backend.app.services.chat.save_message") as mock_save_message, \
         patch("backend.app.services.chat.retrieve_relevant_chunks") as mock_retrieve, \
         patch("backend.app.services.chat.generate_general_answer") as mock_general:

        mock_history.return_value = ""
        mock_retrieve.return_value = [] # No matching placement chunks in DB

        response = process_chat(request=request, current_user=student, db=db_session)

        assert response.answer == "The requested information is not available in the current GCET Knowledge Base."
        mock_general.assert_not_called()


def test_gcet_question_retrieval_429_fails_fast_without_general_ai(db_session, student):
    request = ChatRequest(conversation_id="conv-123", question="What is the minimum attendance at GCET?")

    with patch("backend.app.services.chat.get_conversation_history") as mock_history, \
         patch("backend.app.services.chat.save_message") as mock_save_message, \
         patch("backend.app.services.chat.retrieve_relevant_chunks") as mock_retrieve, \
         patch("backend.app.services.chat.generate_general_answer") as mock_general:

        mock_history.return_value = ""
        mock_retrieve.side_effect = RetrievalServiceError("Rate limited 429")

        response = process_chat(request=request, current_user=student, db=db_session)

        assert "temporarily unavailable" in response.answer.lower()
        mock_general.assert_not_called()


# DIRECT STREAMING TESTS FOR stream_chat()

@pytest.mark.asyncio
async def test_stream_chat_direct_what_is_python(db_session, student):
    mock_request = MagicMock()
    mock_request.is_disconnected = AsyncMock(return_value=False)

    with patch("backend.app.services.chat_stream.get_conversation_history", return_value=""), \
         patch("backend.app.services.chat_stream.retrieve_relevant_chunks") as mock_retrieve, \
         patch("backend.app.services.chat_stream.generate_general_answer_stream") as mock_gen_stream:

        mock_gen_stream.return_value = ["Python ", "is ", "a ", "language."]

        events = await _consume_stream(stream_chat("conv-s1", "What is Python?", student, db_session, mock_request))

        mock_retrieve.assert_not_called()
        done_events = [json.loads(e) for e in events if "type" in e and '"done"' in e]
        assert len(done_events) == 1
        assert done_events[0]["mode"] == "general"


@pytest.mark.asyncio
async def test_stream_chat_direct_package_in_java(db_session, student):
    mock_request = MagicMock()
    mock_request.is_disconnected = AsyncMock(return_value=False)

    with patch("backend.app.services.chat_stream.get_conversation_history", return_value=""), \
         patch("backend.app.services.chat_stream.retrieve_relevant_chunks") as mock_retrieve, \
         patch("backend.app.services.chat_stream.generate_general_answer_stream") as mock_gen_stream:

        mock_gen_stream.return_value = ["A ", "package ", "in ", "Java."]

        events = await _consume_stream(stream_chat("conv-s2", "What is a package in Java?", student, db_session, mock_request))

        mock_retrieve.assert_not_called()
        done_events = [json.loads(e) for e in events if "type" in e and '"done"' in e]
        assert len(done_events) == 1
        assert done_events[0]["mode"] == "general"


@pytest.mark.asyncio
async def test_stream_chat_direct_minimum_attendance(db_session, student):
    mock_request = MagicMock()
    mock_request.is_disconnected = AsyncMock(return_value=False)

    with patch("backend.app.services.chat_stream.get_conversation_history", return_value=""), \
         patch("backend.app.services.chat_stream.retrieve_relevant_chunks") as mock_retrieve, \
         patch("backend.app.services.chat_stream.generate_rag_answer_stream") as mock_rag_stream:

        mock_retrieve.return_value = create_rag_chunks()
        mock_rag_stream.return_value = ["75% ", "attendance ", "required."]

        events = await _consume_stream(stream_chat("conv-s3", "What is the minimum attendance at GCET?", student, db_session, mock_request))

        mock_retrieve.assert_called_once()
        done_events = [json.loads(e) for e in events if "type" in e and '"done"' in e]
        assert len(done_events) == 1
        assert done_events[0]["mode"] == "rag"


@pytest.mark.asyncio
async def test_stream_chat_direct_placement_highest_salary(db_session, student):
    mock_request = MagicMock()
    mock_request.is_disconnected = AsyncMock(return_value=False)

    with patch("backend.app.services.chat_stream.get_conversation_history", return_value=""), \
         patch("backend.app.services.chat_stream.retrieve_relevant_chunks") as mock_retrieve, \
         patch("backend.app.services.chat_stream.generate_rag_answer_stream") as mock_rag_stream, \
         patch("backend.app.services.chat_stream.generate_general_answer_stream") as mock_gen_stream:

        mock_retrieve.return_value = [] # 0 chunks in DB
        mock_gen_stream.return_value = ["General answer"]

        events = await _consume_stream(stream_chat("conv-s4", "Who got the highest salary among 2026 graduates?", student, db_session, mock_request))

        mock_retrieve.assert_called_once()
        mock_gen_stream.assert_not_called()

        token_text = "".join(json.loads(e).get("content", "") for e in events if '"token"' in e)
        assert "The requested information is not available in the current GCET Knowledge Base." in token_text


@pytest.mark.asyncio
async def test_stream_chat_direct_companies_visited(db_session, student):
    mock_request = MagicMock()
    mock_request.is_disconnected = AsyncMock(return_value=False)

    with patch("backend.app.services.chat_stream.get_conversation_history", return_value=""), \
         patch("backend.app.services.chat_stream.retrieve_relevant_chunks") as mock_retrieve, \
         patch("backend.app.services.chat_stream.generate_rag_answer_stream") as mock_rag_stream:

        mock_retrieve.return_value = create_rag_chunks()
        mock_rag_stream.return_value = ["Top ", "companies."]

        events = await _consume_stream(stream_chat("conv-s5", "Which companies visited GCET for placements?", student, db_session, mock_request))

        mock_retrieve.assert_called_once()
        done_events = [json.loads(e) for e in events if "type" in e and '"done"' in e]
        assert len(done_events) == 1
        assert done_events[0]["mode"] == "rag"


@pytest.mark.asyncio
async def test_stream_chat_direct_429_retrieval_unavailable(db_session, student):
    mock_request = MagicMock()
    mock_request.is_disconnected = AsyncMock(return_value=False)

    with patch("backend.app.services.chat_stream.get_conversation_history", return_value=""), \
         patch("backend.app.services.chat_stream.retrieve_relevant_chunks") as mock_retrieve, \
         patch("backend.app.services.chat_stream.generate_general_answer_stream") as mock_gen_stream:

        mock_retrieve.side_effect = RetrievalServiceError("429 Rate Limit")

        events = await _consume_stream(stream_chat("conv-s6", "What is the minimum attendance at GCET?", student, db_session, mock_request))

        mock_gen_stream.assert_not_called()
        done_events = [json.loads(e) for e in events if "type" in e and '"done"' in e]
        assert len(done_events) == 1
        assert done_events[0]["mode"] == "retrieval_unavailable"
