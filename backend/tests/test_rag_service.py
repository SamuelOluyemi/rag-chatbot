from types import SimpleNamespace

from app.services.rag_service import answer_question


def test_answer_question_generates_answer(mocker):
    mock_retrieval = mocker.patch(
        "app.services.rag_service.retrieve_relevant_chunks"
    )

    mock_generation = mocker.patch(
        "app.services.rag_service.generate_answer"
    )

    chunk = SimpleNamespace(
        document_id=1,
        chunk_index=0,
        content="RAG combines retrieval and generation.",
    )

    mock_retrieval.return_value = [
        (chunk, 0.85),
    ]

    mock_generation.return_value = "RAG combines retrieval and generation."

    result = answer_question(
        db=mocker.Mock(),
        user_id=1,
        query="What is RAG?",
    )

    assert result["answer"] == "RAG combines retrieval and generation."
    assert result["sources"] == [
        {
            "document_id": 1,
            "chunk_index": 0,
            "similarity": 0.85,
        }
    ]

    mock_retrieval.assert_called_once()
    mock_generation.assert_called_once()


def test_answer_question_handles_no_relevant_chunks(mocker):
    mock_retrieval = mocker.patch(
        "app.services.rag_service.retrieve_relevant_chunks",
        return_value=[],
    )

    mock_generation = mocker.patch(
        "app.services.rag_service.generate_answer"
    )

    result = answer_question(
        db=mocker.Mock(),
        user_id=1,
        query="What is RAG?",
    )

    assert result == {
        "answer": "I couldn't find relevant information in your documents.",
        "sources": [],
    }

    mock_retrieval.assert_called_once()
    mock_generation.assert_not_called()
    