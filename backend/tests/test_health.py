from app.config import ENV_FILE, Settings
from app.services import providers


def test_health_without_keys_makes_no_provider_calls(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app": "LessonLoop", "environment": "development"}
    providers.request_gemini.assert_not_called()


def test_configuration_status_is_safe_and_does_not_verify_access(client, settings):
    settings.gemini_api_key = "test-secret-do-not-expose"
    settings.gemini_model = "test-model"
    response = client.get("/api/providers/status")
    assert response.status_code == 200
    assert response.json() == {
        "gemini": {"configured": True, "model": "test-model"},
    }
    assert "test-secret" not in response.text
    providers.request_gemini.assert_not_called()


def test_empty_and_whitespace_configuration_is_missing(monkeypatch, tmp_path):
    env = tmp_path / ".env"
    env.write_text("GEMINI_API_KEY=file-key\nGEMINI_MODEL=file-model\n", encoding="utf-8")
    monkeypatch.setenv("GEMINI_API_KEY", "  ")
    monkeypatch.setenv("GEMINI_MODEL", "")
    config = Settings(_env_file=env)
    assert config.gemini_api_key is None
    assert config.gemini_model is None


def test_settings_file_is_absolute_and_environment_takes_priority(monkeypatch, tmp_path):
    assert ENV_FILE.is_absolute()
    assert ENV_FILE.parent.name == "backend"
    env = tmp_path / ".env"
    env.write_text("GEMINI_MODEL=file-model\nGEMINI_API_KEY=file-secret\n", encoding="utf-8")
    monkeypatch.setenv("GEMINI_MODEL", "environment-model")
    config = Settings(_env_file=env)
    assert config.gemini_model == "environment-model"
    assert config.gemini_api_key.get_secret_value() == "file-secret"
    assert "file-secret" not in repr(config)


def test_explicit_cors_origin(client):
    allowed = client.options("/api/providers/gemini/check", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"})
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:5173"
    denied = client.options("/api/providers/gemini/check", headers={"Origin": "https://untrusted.example", "Access-Control-Request-Method": "POST"})
    assert "access-control-allow-origin" not in denied.headers
