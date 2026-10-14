from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# ClaimIQ project root directory
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # Application configuration
    app_name: str = "Claims AI Platform"
    env: str = "dev"

    # PostgreSQL database configuration
    database_url: str = (
        "postgresql+psycopg://"
        "claimiq_user:claimiq_password"
        "@localhost:5432/claimiq"
    )

    # JWT authentication configuration
    jwt_secret: str = "claimiq-development-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30

    # Document and AI configuration
    document_dir: str = "./data/documents"
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_api_url: str | None = None
    llm_api_key: str | None = None

    # Claim SLA configuration
    sla_hours: int = 72

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()