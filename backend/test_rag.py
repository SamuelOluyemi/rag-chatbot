
from sqlalchemy import select

from app.db.models import User
from app.db.session import SessionLocal
from app.services.rag_service import answer_question


def test_rag_pipeline():
    db = SessionLocal()

    try:
        # Find the development user.
        user = db.scalar(
            select(User).where(
                User.email == "local@ragchatbot.local"
            )
        )

        if user is None:
            raise RuntimeError("Development user not found.")

        # Ask a question about the uploaded PDF.
        query = "What is this document about?"

        print("Question:", query)
        print("\nRunning complete RAG pipeline...\n")

        result = answer_question(
            db=db,
            user_id=user.id,
            query=query,
        )

        print("Generated answer:")
        print(result["answer"])

        print("\nRetrieved sources:")

        for source in result["sources"]:
            print(
                f"Document ID: {source['document_id']}, "
                f"Chunk: {source['chunk_index']}, "
                f"Similarity: {source['similarity']}"
            )

        print("\nRAG pipeline test completed!")

    finally:
        db.close()


if __name__ == "__main__":
    test_rag_pipeline()

