
from functools import lru_cache

from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Load and cache the local sentence embedding model."""

    return SentenceTransformer(MODEL_NAME)


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate vector embeddings for a list of text chunks.

    Args:
        texts: A list of text strings.

    Returns:
        A list of 384-dimensional embedding vectors.
    """

    if not texts:
        return []

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
    )

    return embeddings.tolist()
