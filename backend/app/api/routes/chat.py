
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import answer_question


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    """Answer a user's question using their uploaded documents."""

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

    try:
        result = answer_question(
            db=db,
            user_id=user.id,
            query=request.question,
        )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError:
        raise HTTPException(
            status_code=503,
            detail="The answer generation service is currently unavailable.",
        )
