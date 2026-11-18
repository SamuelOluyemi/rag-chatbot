from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app


@pytest.fixture
def client():
    mock_db = Mock()

    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client, mock_db

    app.dependency_overrides.clear()


def test_health_endpoint(client):
    test_client, _ = client

    response = test_client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_chat_endpoint_returns_answer(client, mocker):
    test_client, mock_db = client

    mock_db.scalar.return_value = SimpleNamespace(id=1)

    mocker.patch(
        "app.api.routes.chat.answer_question",
        return_value={
            "answer": "RAG combines retrieval and generation.",
            "sources": [
                {
                    "document_id": 1,
                    "chunk_index": 0,
                    "similarity": 0.85,
                }
            ],
        },
    )

    response = test_client.post(
        "/api/chat/",
        json={"question": "What is RAG?"},
    )

    assert response.status_code == 200
    assert response.json()["answer"] == (
        "RAG combines retrieval and generation."
    )
    assert len(response.json()["sources"]) == 1


def test_chat_endpoint_handles_missing_user(client):
    test_client, mock_db = client

    mock_db.scalar.return_value = None

    response = test_client.post(
        "/api/chat/",
        json={"question": "What is RAG?"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Development user not found."


def test_chat_endpoint_handles_invalid_question(client, mocker):
    test_client, mock_db = client

    mock_db.scalar.return_value = SimpleNamespace(id=1)

    mocker.patch(
        "app.api.routes.chat.answer_question",
        side_effect=ValueError("Invalid question."),
    )

    response = test_client.post(
        "/api/chat/",
        json={"question": "What is RAG?"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid question."


def test_chat_endpoint_handles_generation_failure(client, mocker):
    test_client, mock_db = client

    mock_db.scalar.return_value = SimpleNamespace(id=1)

    mocker.patch(
        "app.api.routes.chat.answer_question",
        side_effect=RuntimeError("Ollama unavailable."),
    )

    response = test_client.post(
        "/api/chat/",
        json={"question": "What is RAG?"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "The answer generation service is currently unavailable."
    )


def test_chat_endpoint_rejects_empty_question(client):
    test_client, mock_db = client

    response = test_client.post(
        "/api/chat/",
        json={"question": ""},
    )

    assert response.status_code == 422
    mock_db.scalar.assert_not_called()
    