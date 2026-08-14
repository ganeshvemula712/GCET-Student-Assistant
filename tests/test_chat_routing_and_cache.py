from unittest.mock import MagicMock, patch
import pytest
from google.genai.errors import APIError

from backend.app.schemas.chat import ChatRequest
from backend.app.services.embeddings import generate_embeddings, generate_query_embedding, _cached_query_embedding
from backend.app.services.retrieval import RetrievalServiceError, retrieve_relevant_chunks
from backend.app.services.chat import process_chat
from tests.fixtures.chat import create_rag_chunks


def setup_function():
    # Clear query embedding cache before each test
    _cached_query_embedding.cache_clear()


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


def test_general_question_bypasses_vector_retrieval(db_session, student):
    request = ChatRequest(conversation_id="conv-123", question="What is Python?")

    with patch("backend.app.services.chat.get_conversation_history") as mock_history, \
         patch("backend.app.services.chat.save_message") as mock_save_message, \
         patch("backend.app.services.chat.retrieve_relevant_chunks") as mock_retrieve, \
         patch("backend.app.services.chat.generate_general_answer") as mock_general:

        mock_history.return_value = ""
        mock_general.return_value = ("Python is a high-level programming language.", 85, [])

        response = process_chat(request=request, current_user=student, db=db_session)

        assert response.answer == "Python is a high-level programming language."
        # Retrieval MUST be bypassed completely
        mock_retrieve.assert_not_called()


def test_gcet_question_executes_retrieval(db_session, student):
    request = ChatRequest(conversation_id="conv-123", question="What is the minimum attendance at GCET?")

    with patch("backend.app.services.chat.get_conversation_history") as mock_history, \
         patch("backend.app.services.chat.save_message") as mock_save_message, \
         patch("backend.app.services.chat.retrieve_relevant_chunks") as mock_retrieve, \
         patch("backend.app.services.chat.generate_rag_answer") as mock_rag:

        mock_history.return_value = ""
        mock_retrieve.return_value = create_rag_chunks()
        mock_rag.return_value = ("Minimum attendance requirement is 75%.", 90, [])

        response = process_chat(request=request, current_user=student, db=db_session)

        assert response.answer == "Minimum attendance requirement is 75%."
        mock_retrieve.assert_called_once()


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
        # General AI LLM must NOT be called for ungrounded GCET question!
        mock_general.assert_not_called()
