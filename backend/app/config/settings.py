"""Environment-backed application settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated runtime configuration sourced from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "RepoMind API"
    app_version: str = "0.1.0"
    environment: Literal["local", "development", "staging", "production"] = "local"
    log_level: str = "INFO"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    api_v1_prefix: str = "/api"
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"]
    )
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/repomind"
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10
    git_executable: str = "git"
    ingestion_max_file_size_bytes: int = 1_048_576
    embedding_model: str = "all-minilm:l6-v2"
    embedding_base_url: str = "http://localhost:11434"
    # Vector width for embedding_model (all-minilm:l6-v2 -> 384). Sizes the pgvector
    # column; changing to a model with a different width requires a new migration.
    embedding_dimensions: int = 384
    generation_model: str = "llama3.2"
    generation_base_url: str = "http://localhost:11434"
    # Public key endpoint for verifying Clerk-issued session JWTs (not a secret).
    # Find it under your Clerk instance's Frontend API settings, e.g.
    # https://<your-instance>.clerk.accounts.dev/.well-known/jwks.json
    clerk_jwks_url: str = ""
    clerk_issuer: str | None = None

    @property
    def debug(self) -> bool:
        return self.environment in {"local", "development"}


@lru_cache
def get_settings() -> Settings:
    """Return a process-wide immutable settings instance."""
    return Settings()
