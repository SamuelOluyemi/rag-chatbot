
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.models import User
from app.db.session import get_db
from app.services.ingestion_service import ingest_pdf


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

UPLOAD_DIR = Path("backend/uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload, validate, and ingest a PDF document."""

    # Validate the uploaded file's extension.
    if Path(file.filename or "").suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    # Validate the uploaded file's content type.
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Invalid file content type. Please upload a PDF.",
        )

    # Find the development user.
    user = db.scalar(
        select(User).where(
            User.email == "local@ragchatbot.local"
        )
    )

    if user is None:
        raise HTTPException(
            status_code=500,
            detail="Development user not found.",
        )

    # Create the upload directory if necessary.
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Generate a unique server-side filename.
    stored_filename = f"{uuid4().hex}.pdf"
    file_path = UPLOAD_DIR / stored_filename

    try:
        # Save the uploaded file while enforcing the size limit.
        total_size = 0

        with file_path.open("wb") as uploaded_file:
            while chunk := await file.read(1024 * 1024):
                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="File size exceeds the 10 MB limit.",
                    )

                uploaded_file.write(chunk)

        # Process the PDF and persist its document and chunks.
        document = ingest_pdf(
            db=db,
            user_id=user.id,
            file_path=file_path,
            filename=file.filename or stored_filename,
            content_type=file.content_type,
        )

        return {
            "message": "File uploaded and processed successfully.",
            "document_id": document.id,
            "filename": document.filename,
            "stored_filename": stored_filename,
            "size_bytes": total_size,
        }

    except HTTPException:
        file_path.unlink(missing_ok=True)
        raise

    except ValueError as exc:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    except IntegrityError:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=409,
            detail="This document has already been uploaded.",
        )

    except Exception:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail="Document upload or processing failed.",
        )

    finally:
        await file.close()
