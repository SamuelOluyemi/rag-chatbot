
from sqlalchemy import select

from app.db.models import User, Document, DocumentChunk
from app.db.session import SessionLocal
from app.services.ingestion_service import ingest_pdf


def test_pdf_ingestion():
    db = SessionLocal()

    try:
        # Find our existing development user.
        user = db.scalar(
            select(User).where(
                User.email == "local@ragchatbot.local"
            )
        )

        if user is None:
            raise RuntimeError("Development user not found.")

        # Ingest the sample PDF.
        document = ingest_pdf(
            db=db,
            user_id=user.id,
            file_path="backend/uploads/LLM Test Doc.pdf",
            filename="LLM Test Doc.pdf",
        )

        # Retrieve the document's stored chunks.
        chunks = db.scalars(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document.id)
            .order_by(DocumentChunk.chunk_index)
        ).all()

        print("Document ingestion successful!")
        print("Document ID:", document.id)
        print("Filename:", document.filename)
        print("Number of chunks:", len(chunks))
        print("First chunk:", chunks[0].content)
        print("Embedding dimensions:", len(chunks[0].embedding))

    finally:
        db.close()


if __name__ == "__main__":
    test_pdf_ingestion()
