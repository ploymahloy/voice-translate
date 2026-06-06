from server.config import cors_allow_origins

def test_cors_allow_origins_default_when_unset(monkeypatch):
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    assert cors_allow_origins() == [
        "http://localhost:4321",
        "https://voice-translate-flax.vercel.app",
    ]

def test_cors_allow_origins_single_origin(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "https://app.example.com")
    assert cors_allow_origins() == ["https://app.example.com"]

def test_cors_allow_origins_multiple_with_whitespace(monkeypatch):
    monkeypatch.setenv(
        "CORS_ORIGINS",
        " https://app.example.com , http://localhost:4321 ",
    )
    assert cors_allow_origins() == [
        "https://app.example.com",
        "http://localhost:4321",
    ]
