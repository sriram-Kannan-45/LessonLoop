from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Provider(str, Enum):
    gemini = "gemini"


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    app: str
    environment: str


class ProviderStatus(BaseModel):
    configured: bool
    model: str | None


class ProvidersStatus(BaseModel):
    gemini: ProviderStatus


class CheckSuccess(BaseModel):
    provider: Provider
    status: Literal["success"] = "success"
    model: str
    message: str = Field(min_length=1, max_length=500)
    latency_ms: int = Field(ge=0)
    checked_at: datetime


class CheckError(BaseModel):
    provider: Provider
    status: Literal["error"] = "error"
    error_code: str
    message: str
