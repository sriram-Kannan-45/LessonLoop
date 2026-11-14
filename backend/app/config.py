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
    provider_timeout_seconds: float = Field(default=30, gt=0, le=120)
    workflow_timeout_seconds: float = Field(default=90, gt=0, le=180)
    technical_retries: int = Field(default=2, ge=0, le=2)
    database_path: Path = ENV_FILE.parent / "data" / "lessonloop.sqlite3"

    @field_validator("gemini_api_key", "gemini_model", "gemini_evaluator_model", mode="before")
    @classmethod
    def empty_is_missing(cls, value):
        if isinstance(value, str):
            return value.strip() or None
        return value

    @field_validator("database_path")
    @classmethod
    def resolve_database_path(cls, value):
        return value if value.is_absolute() else ENV_FILE.parent / value


@lru_cache
def get_settings() -> Settings:
    return Settings()
