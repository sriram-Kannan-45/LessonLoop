from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore",
        env_ignore_empty=False, validate_assignment=True,
    )

    app_name: str = "LessonLoop"
    app_env: str = "development"
    backend_host: str = "127.0.0.1"
    backend_port: int = Field(default=8000, ge=1, le=65535)
    frontend_origin: str = "http://localhost:5173"
    gemini_api_key: SecretStr | None = None
    gemini_model: str | None = None
    gemini_evaluator_model: str | None = None
    groq_api_key: SecretStr | None = None
    groq_model: str = "qwen/qwen3.8-27b"
    groq_evaluator_model: str | None = None
    groq_fallback_enabled: bool = True
    groq_min_interval_seconds: float = Field(default=65, ge=0, le=120)
    freellm_base_url: str = "http://127.0.0.1:31415/v1"
    freellm_api_key: SecretStr | None = None
    freellm_model: str = "auto"
    freellm_evaluator_model: str | None = None
    freellm_fallback_enabled: bool = True
    freellm_max_output_tokens: int = Field(default=8192, ge=512, le=32768)
    provider_timeout_seconds: float = Field(default=30, gt=0, le=120)
    workflow_timeout_seconds: float = Field(default=90, gt=0, le=180)
    technical_retries: int = Field(default=2, ge=0, le=2)
    database_path: Path = ENV_FILE.parent / "data" / "lessonloop.sqlite3"

    @field_validator("gemini_api_key", "gemini_model", "gemini_evaluator_model", "groq_api_key", "groq_evaluator_model", "freellm_api_key", "freellm_evaluator_model", mode="before")
    @classmethod
    def empty_is_missing(cls, value):
        if isinstance(value, str):
            return value.strip() or None
        return value

    @field_validator("freellm_base_url")
    @classmethod
    def valid_router_url(cls, value):
        from urllib.parse import urlsplit
        value = value.strip().rstrip("/")
        parts = urlsplit(value)
        if parts.username or parts.password or parts.query or parts.fragment or not parts.hostname:
            raise ValueError("Use a base URL without credentials, query or fragment")
        if parts.scheme != "https" and not (parts.scheme == "http" and parts.hostname in {"localhost", "127.0.0.1", "::1"}):
            raise ValueError("Use HTTPS or a loopback HTTP service")
        return value

    @field_validator("database_path")
    @classmethod
    def resolve_database_path(cls, value):
        return value if value.is_absolute() else ENV_FILE.parent / value


@lru_cache
def get_settings() -> Settings:
    return Settings()
