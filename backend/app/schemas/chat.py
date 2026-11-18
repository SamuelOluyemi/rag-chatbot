
from pydantic import BaseModel, Field

# Add the chat request schema
class ChatRequest(BaseModel):
    """Validate incoming chat questions."""

    question: str = Field(
        min_length=1,
        max_length=2000,
        description="The user's question about their uploaded documents.",
    )

# Add the chat response schema
class ChatSource(BaseModel):
    """Represent a document chunk used to generate an answer."""

    document_id: int
    chunk_index: int
    similarity: float

class ChatResponse(BaseModel):
    """Structure the chatbot's response."""

    answer: str
    sources: list[ChatSource]
