
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models import Document, DocumentChunk, User
from app.services.pdf_service import extract_text_from_pdf
from app.services.chunking_service import split_text_into_chunks
from app.services.embedding_service import generate_embeddings

from sqlalchemy import select

from app.services.file_service import calculate_file_hash


def ingest_pdf(
    db: Session,
    user_id: int,
    file_path: str | Path,
    filename: str,
    content_type: str = "application/pdf",
) -> Document:
    """
    Extract, chunk, embed, and store a PDF document.

    Args:
        db: Active SQLAlchemy database session.
        user_id: ID of the user who owns the document.
        file_path: Location of the PDF file.
        filename: Original document filename.
        content_type: MIME type of the uploaded document.

    Returns:
        The saved Document object.

    Raises:
        ValueError: If the user does not exist or no chunks are produced.
        FileNotFoundError: If the PDF does not exist.
        Exception: If ingestion or database persistence fails.
    """

    try:
        # 1. Verify that the document owner exists.
        user = db.get(User, user_id)

        if user is None:
            raise ValueError(f"User with ID {user_id} does not exist.")
        
        # Calculate the SHA-256 hash of the uploaded file.
        file_hash = calculate_file_hash(file_path)

        # Check whether this user has already uploaded this file.
        existing_document = db.scalar(
            select(Document).where(
                Document.user_id == user_id,
                Document.file_hash == file_hash,
            )
        )

        if existing_document is not None:
            raise ValueError(
                "This document has already been uploaded."
            )

        # 2. Extract text from the PDF.
        extracted_text = extract_text_from_pdf(file_path)

        # 3. Split the extracted text into chunks.
        chunks = split_text_into_chunks(extracted_text)

        if not chunks:
            raise ValueError("No text chunks were generated.")

        # 4. Generate embeddings for all chunks.
        embeddings = generate_embeddings(chunks)

        # 5. Create the document record.
        document = Document(
            user_id=user_id,
            filename=filename,
            file_path=str(file_path),
            file_hash=file_hash,
            content_type=content_type,
        )

        db.add(document)
        db.flush()

        # 6. Create database records for each chunk and embedding.
        document_chunks = [
            DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk,
                embedding=embedding,
            )
            for index, (chunk, embedding) in enumerate(
                zip(chunks, embeddings)
            )
        ]

        db.add_all(document_chunks)

        # 7. Commit everything as one transaction.
        db.commit()
        db.refresh(document)

        return document

    except Exception:
        db.rollback()
        raise
