import os

SUPPORTED_LANGUAGES: frozenset[str] = frozenset({"en", "es", "fr", "de"})

ALLOWED_AUDIO_EXTENSIONS: frozenset[str] = frozenset(
    {".wav", ".mp3", ".m4a", ".ogg", ".webm"}
)

_DEFAULT_MAX_UPLOAD_BYTES = 25 * 1024 * 1024

def max_upload_bytes() -> int:
    raw = os.environ.get("MAX_UPLOAD_BYTES", str(_DEFAULT_MAX_UPLOAD_BYTES))
    return int(raw)

def service_api_key() -> str:
    return os.environ.get("SERVICE_API_KEY", "").strip()

_DEFAULT_CORS_ORIGINS = ("http://localhost:4321",)

def cors_allow_origins() -> list[str]:
    raw = os.environ.get("CORS_ORIGINS", "").strip()
    if not raw:
        return list(_DEFAULT_CORS_ORIGINS)
    return [origin.strip() for origin in raw.split(",") if origin.strip()]
