from fastapi import FastAPI

from app.core.config import get_settings
from app.api.routes.documents import router as documents_router
from app.api.routes.chat import router as chat_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Return the application's health status."""
    return {
        "status": "healthy",
        "application": settings.app_name,
        "environment": settings.environment,
    }

# Document routes
app.include_router(
    documents_router,
    prefix="/api",
)

# Chat routes
app.include_router(
    chat_router,
    prefix="/api",
)