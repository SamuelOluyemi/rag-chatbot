
from sqlalchemy import select
from sentence_transformers import SentenceTransformer

from app.db.session import SessionLocal
from app.db.models import User, Document, DocumentChunk


def test_database_operations():
    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    db = SessionLocal()

    try:
        # Retrieve the local development user.
        user = db.scalar(
            select(User).where(
                User.email == "local@ragchatbot.local"
            )
        )

        if user is None:
            raise RuntimeError("Development user not found.")

        # Create a document belonging to the user.
        document = Document(
            user_id=user.id,
            filename="test-document.txt",
            file_path="uploads/test-document.txt",
            content_type="text/plain",
        )

        db.add(document)
        db.flush()

        # Generate an embedding for a sample text chunk.
        content = (
            "Retrieval-Augmented Generation uses "
            "document retrieval to answer questions."
        )

        embedding = model.encode(content).tolist()

        # Store the chunk and its embedding.
        chunk = DocumentChunk(
            document_id=document.id,
            chunk_index=0,
            content=content,
            embedding=embedding,
        )

        db.add(chunk)
        db.flush()

        # Retrieve the stored chunk.
        retrieved = db.scalar(
            select(DocumentChunk).where(
                DocumentChunk.document_id == document.id
            )
        )

        print("User:", user.email)
        print("Document ID:", document.id)
        print("Chunk ID:", retrieved.id)
        print("Chunk content:", retrieved.content)
        print("Embedding dimensions:", len(retrieved.embedding))
        print("Database operations successful!")

    finally:
        # Undo test inserts so the database stays clean.
        db.rollback()
        db.close()


if __name__ == "__main__":
    test_database_operations()
