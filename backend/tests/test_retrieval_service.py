from types import SimpleNamespace

import pytest

from app.services.retrieval_service import retrieve_relevant_chunks


def test_retrieve_relevant_chunks_returns_results(mocker):
    mock_embedding = mocker.patch(
        "app.services.retrieval_service.generate_embeddings",
        return_value=[[0.1, 0.2, 0.3]],
    )

    chunk = SimpleNamespace(
        id=1,
        document_id=1,
        chunk_index=0,
        content="RAG combines retrieval and generation.",
    )

    mock_db = mocker.Mock()
    mock_db.execute.return_value.all.return_value = [
        (chunk, 0.85),
    ]

    results = retrieve_relevant_chunks(
        db=mock_db,
        user_id=1,
        query="What is RAG?",
    )

    assert len(results) == 1
    assert results[0][0] is chunk
    assert results[0][1] == 0.85

    mock_embedding.assert_called_once_with(["What is RAG?"])
    mock_db.execute.assert_called_once()


def test_retrieve_relevant_chunks_rejects_empty_query():
    with pytest.raises(ValueError, match="Search query cannot be empty"):
        retrieve_relevant_chunks(
            db=None,
            user_id=1,
            query=" ",
        )


def test_retrieve_relevant_chunks_rejects_invalid_top_k():
    with pytest.raises(ValueError, match="top_k must be greater than zero"):
        retrieve_relevant_chunks(
            db=None,
            user_id=1,
            query="What is RAG?",
            top_k=0,
        )


def test_retrieve_relevant_chunks_filters_by_user(mocker):
    mocker.patch(
        "app.services.retrieval_service.generate_embeddings",
        return_value=[[0.1, 0.2, 0.3]],
    )

    mock_db = mocker.Mock()
    mock_db.execute.return_value.all.return_value = []

    retrieve_relevant_chunks(
        db=mock_db,
        user_id=42,
        query="What is RAG?",
    )

    statement = mock_db.execute.call_args.args[0]
    compiled_statement = str(statement)

    assert "documents.user_id" in compiled_statement
    