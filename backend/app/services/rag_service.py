
from sqlalchemy.orm import Session

from app.services.retrieval_service import retrieve_relevant_chunks
from app.services.generation_service import generate_answer


def answer_question(
    db: Session,
    user_id: int,
    query: str,
    top_k: int = 5,
) -> dict:
    """
    Answer a user's question using their uploaded documents.

    Retrieves relevant document chunks and passes them
    to the local language model for answer generation.
    """

    # 1. Retrieve relevant document chunks.
    results = retrieve_relevant_chunks(
        db=db,
        user_id=user_id,
        query=query,
        top_k=top_k,
    )

    # 2. Handle cases where no relevant chunks are found.
    if not results:
        return {
            "answer": "I couldn't find relevant information in your documents.",
            "sources": [],
        }

    # 3. Extract the text content from retrieved chunks.
    context = [
        chunk.content
        for chunk, similarity in results
    ]

    # 4. Generate an answer using the retrieved context.
    answer = generate_answer(
        query=query,
        context=context,
    )

    # 5. Return the answer and its source information.
    sources = [
        {
            "document_id": chunk.document_id,
            "chunk_index": chunk.chunk_index,
            "similarity": round(similarity, 4),
        }
        for chunk, similarity in results
    ]

    return {
        "answer": answer,
        "sources": sources,
    }

