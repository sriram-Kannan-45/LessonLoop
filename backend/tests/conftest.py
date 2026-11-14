from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import create_app
from app.services import providers
from app.services import groq
from app.services.lesson_ai import LessonAI


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch):
    for name in Settings.model_fields:
        monkeypatch.delenv(name.upper(), raising=False)
    get_settings.cache_clear()
    # Fail immediately if a route unexpectedly attempts an external request.
    monkeypatch.setattr(providers, "request_gemini", AsyncMock(side_effect=AssertionError("Network calls are forbidden in tests")))
    monkeypatch.setattr(LessonAI, "generate", AsyncMock(side_effect=AssertionError("Network calls are forbidden in tests")))
    monkeypatch.setattr(LessonAI, "evaluate", AsyncMock(side_effect=AssertionError("Network calls are forbidden in tests")))
    monkeypatch.setattr(groq, "request_groq", AsyncMock(side_effect=AssertionError("Network calls are forbidden in tests")))
    yield
    get_settings.cache_clear()


@pytest.fixture
def settings(tmp_path):
    return Settings(_env_file=None, database_path=tmp_path / "test.sqlite3")


@pytest.fixture
def client(settings):
    app = create_app(settings=settings)
    app.dependency_overrides[get_settings] = lambda: settings
    with TestClient(app) as test_client:
        yield test_client
