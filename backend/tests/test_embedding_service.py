from unittest.mock import MagicMock

from app.services.embedding_service import (
    generate_embeddings,
    get_embedding_model,
)


def test_generate_embeddings_returns_vectors(mocker):
    mock_model = MagicMock()
    mock_model.encode.return_value.tolist.return_value = [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ]

    mocker.patch(
        "app.services.embedding_service.get_embedding_model",
        return_value=mock_model,
    )

    embeddings = generate_embeddings(["First text", "Second text"])

    assert len(embeddings) == 2
    assert embeddings[0] == [0.1, 0.2, 0.3]
    assert embeddings[1] == [0.4, 0.5, 0.6]


def test_generate_embeddings_returns_empty_list():
    assert generate_embeddings([]) == []


def test_get_embedding_model_is_cached(mocker):
    mock_model_class = mocker.patch(
        "app.services.embedding_service.SentenceTransformer"
    )

    get_embedding_model.cache_clear()

    first_model = get_embedding_model()
    second_model = get_embedding_model()

    assert first_model is second_model
    mock_model_class.assert_called_once()

    get_embedding_model.cache_clear()
    