from server.main import create_app
from fastapi.testclient import TestClient

def _client(monkeypatch, origins: str) -> TestClient:
    monkeypatch.setenv("CORS_ORIGINS", origins)
    return TestClient(create_app())

def test_preflight_allowed_origin(monkeypatch):
    client = _client(monkeypatch, "https://app.example.com")
    response = client.options(
        "/health",
        headers={
            "Origin": "https://app.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "https://app.example.com"

def test_preflight_disallowed_origin(monkeypatch):
    client = _client(monkeypatch, "https://app.example.com")
    response = client.options(
        "/health",
        headers={
            "Origin": "https://evil.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 400
    assert response.headers.get("access-control-allow-origin") is None

def test_get_with_allowed_origin(monkeypatch):
    client = _client(monkeypatch, "https://app.example.com")
    response = client.get("/health", headers={"Origin": "https://app.example.com"})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "https://app.example.com"

def test_translate_preflight_allows_post_and_api_key_header(monkeypatch):
    client = _client(monkeypatch, "https://app.example.com")
    response = client.options(
        "/translate",
        headers={
            "Origin": "https://app.example.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "x-api-key",
        },
    )
    assert response.status_code == 200
    allow_methods = response.headers.get("access-control-allow-methods", "")
    assert "POST" in allow_methods
    allow_headers = response.headers.get("access-control-allow-headers", "").lower()
    assert "x-api-key" in allow_headers

def test_preflight_vercel_origin_with_default_config(monkeypatch):
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    client = TestClient(create_app())
    response = client.options(
        "/health",
        headers={
            "Origin": "https://voice-translate-flax.vercel.app",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert (
        response.headers.get("access-control-allow-origin")
        == "https://voice-translate-flax.vercel.app"
    )
