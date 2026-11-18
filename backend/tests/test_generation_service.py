import httpx
import pytest

from app.services.generation_service import generate_answer


def test_generate_answer_returns_response(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        "response": "RAG combines retrieval with generation."
    }

    mocker.patch(
        "app.services.generation_service.httpx.post",
        return_value=mock_response,
    )

    mock_response.raise_for_status.return_value = None

    answer = generate_answer(
        query="What is RAG?",
        context=["RAG retrieves relevant information from documents."],
    )

    assert answer == "RAG combines retrieval with generation."


def test_generate_answer_returns_message_when_context_is_empty():
    answer = generate_answer(
        query="What is RAG?",
        context=[],
    )

    assert answer == "I couldn't find relevant information in your documents."


def test_generate_answer_rejects_empty_query():
    with pytest.raises(ValueError, match="Query cannot be empty"):
        generate_answer(
            query=" ",
            context=["Some document context."],
        )


def test_generate_answer_handles_http_errors(mocker):
    mocker.patch(
        "app.services.generation_service.httpx.post",
        side_effect=httpx.ConnectError("Connection failed"),
    )

    with pytest.raises(RuntimeError, match="Failed to communicate with Ollama"):
        generate_answer(
            query="What is RAG?",
            context=["Some document context."],
        )
        