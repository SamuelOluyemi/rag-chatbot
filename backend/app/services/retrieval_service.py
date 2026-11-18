
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Document, DocumentChunk
from app.services.embedding_service import generate_embeddings


def retrieve_relevant_chunks(
    db: Session,
    user_id: int,
    query: str,
    top_k: int = 5,
) -> list[tuple[DocumentChunk, float]]:
    """
    Retrieve the most relevant document chunks for a query.

    Args:
        db: Active SQLAlchemy database session.
        user_id: ID of the user performing the search.
        query: User's question or search text.
        top_k: Maximum number of chunks to retrieve.

    Returns:
        A list of (DocumentChunk, similarity_score) tuples,
        ordered from most relevant to least relevant.
    """

    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    # 1. Convert the user's query into an embedding.
    query_embedding = generate_embeddings([query])[0]

    # 2. Calculate cosine distance between stored vectors and the query.
    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    )

    # 3. Convert cosine distance into a similarity score.
    similarity = (1 - distance).label("similarity")

    # 4. Retrieve the closest chunks belonging to this user.
    statement = (
        select(DocumentChunk, similarity)
        .join(
            Document,
            DocumentChunk.document_id == Document.id,
        )
        .where(Document.user_id == user_id)
        .order_by(distance)
        .limit(top_k)
    )

    results = db.execute(statement).all()

    return [
        (chunk, float(score))
        for chunk, score in results
    ]
