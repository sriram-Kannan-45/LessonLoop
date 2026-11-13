from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import create_app
from app.services import providers


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch):
    for name in Settings.model_fields:
        monkeypatch.delenv(name.upper(), raising=False)
    get_settings.cache_clear()
    # Fail immediately if a route unexpectedly attempts an external request.
    for provider in ("gemini", "openai"):
        monkeypatch.setattr(providers, f"request_{provider}", AsyncMock(side_effect=AssertionError("Network calls are forbidden in tests")))
    yield
    get_settings.cache_clear()


@pytest.fixture
def settings():
    return Settings(_env_file=None)


@pytest.fixture
def client(settings):
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: settings
    with TestClient(app) as test_client:
        yield test_client
