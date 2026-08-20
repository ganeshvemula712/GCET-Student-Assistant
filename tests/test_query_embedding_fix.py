from unittest.mock import MagicMock, patch
import pytest
from google.genai.errors import APIError

from backend.app.services.embeddings import generate_embeddings
from backend.app.services.retrieval import RetrievalServiceError, retrieve_relevant_chunks


def test_normal_query_embedding_succeeds():
    mock_response = MagicMock()
    mock_vector = MagicMock()
    mock_vector.values = [0.1] * 3072
    mock_response.embeddings = [mock_vector]

    with patch("backend.app.services.embeddings.client.models.embed_content") as mock_embed:
        mock_embed.return_value = mock_response

        res = generate_embeddings(["Test Question"], max_retries=1, retry_delay=0.1)

    assert len(res) == 1
    assert len(res[0]) == 3072
    mock_embed.assert_called_once()


def test_query_embedding_receives_429_once_and_succeeds_on_retry():
    mock_response = MagicMock()
    mock_vector = MagicMock()
    mock_vector.values = [0.2] * 3072
    mock_response.embeddings = [mock_vector]

    error_429 = APIError(429, {"message": "RESOURCE_EXHAUSTED"})

    with patch("backend.app.services.embeddings.client.models.embed_content") as mock_embed, patch("time.sleep") as mock_sleep:
        mock_embed.side_effect = [error_429, mock_response]

        res = generate_embeddings(["Test Question"], max_retries=2, retry_delay=0.1)

    assert len(res) == 1
    assert mock_embed.call_count == 2
    mock_sleep.assert_called_with(0.1)


def test_query_embedding_receives_429_twice_and_fails_quickly():
    error_429 = APIError(429, {"message": "RESOURCE_EXHAUSTED"})

    with patch("backend.app.services.embeddings.client.models.embed_content") as mock_embed, patch("time.sleep") as mock_sleep:
        mock_embed.side_effect = [error_429, error_429]

        with pytest.raises(APIError):
            generate_embeddings(["Test Question"], max_retries=1, retry_delay=0.1)

    assert mock_embed.call_count == 1
    mock_sleep.assert_not_called()


def test_retrieval_handles_embedding_failure_fast():
    error_429 = APIError(429, {"message": "RESOURCE_EXHAUSTED"})

    with patch("backend.app.services.embeddings.client.models.embed_content") as mock_embed, patch("time.sleep") as mock_sleep:
        mock_embed.side_effect = [error_429, error_429]

        with pytest.raises(RetrievalServiceError):
            retrieve_relevant_chunks("What is the minimum attendance?", n_results=4)

    assert mock_embed.call_count == 2
    mock_sleep.assert_called_with(1.0)


def test_document_ingestion_embedding_retains_default_retries():
    mock_response = MagicMock()
    mock_vector = MagicMock()
    mock_vector.values = [0.3] * 3072
    mock_response.embeddings = [mock_vector]

    with patch("backend.app.services.embeddings.client.models.embed_content") as mock_embed:
        mock_embed.return_value = mock_response

        res = generate_embeddings(["Chunk 1", "Chunk 2"])

    assert len(res) == 2
    assert mock_embed.call_count == 2
