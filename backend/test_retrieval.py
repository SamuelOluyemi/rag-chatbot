
from sqlalchemy import select

from app.db.models import User
from app.db.session import SessionLocal
from app.services.retrieval_service import retrieve_relevant_chunks


def test_semantic_retrieval():
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

        # Search the user's documents.
        query = "What is this document about?"

        results = retrieve_relevant_chunks(
            db=db,
            user_id=user.id,
            query=query,
            top_k=5,
        )

        print("Search query:", query)
        print("Number of results:", len(results))

        for index, (chunk, similarity) in enumerate(results, 1):
            print(f"\nResult {index}")
            print("Document ID:", chunk.document_id)
            print("Chunk:", chunk.content)
            print("Similarity score:", round(similarity, 4))

        print("\nSemantic retrieval test completed!")

    finally:
        db.close()


if __name__ == "__main__":
    test_semantic_retrieval()
