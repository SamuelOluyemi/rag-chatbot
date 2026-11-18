
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = "RAG Chatbot"
    environment: str = "development"

    openai_api_key: SecretStr | None = None

    database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5433/ragchatbot"
    )

    model_config = SettingsConfigDict(
        env_file="backend/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached application settings instance."""
    return Settings()
