import json
import os

from server.env import project_root

_LANGUAGES_PATH = project_root() / "shared" / "languages.json"


def _load_languages() -> tuple[tuple[str, str], ...]:
    raw = json.loads(_LANGUAGES_PATH.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError(f"{_LANGUAGES_PATH}: expected a JSON array")

    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError(f"{_LANGUAGES_PATH}: each entry must be an object")
        code = item.get("code")
        label = item.get("label")
        if not isinstance(code, str) or not isinstance(label, str):
            raise ValueError(f"{_LANGUAGES_PATH}: each entry needs string code and label")
        if code in seen:
            raise ValueError(f"{_LANGUAGES_PATH}: duplicate language code {code!r}")
        seen.add(code)
        entries.append((code, label))

    return tuple(entries)


_LANGUAGES = _load_languages()
SUPPORTED_LANGUAGES: frozenset[str] = frozenset(code for code, _ in _LANGUAGES)
LANGUAGE_LABELS: dict[str, str] = dict(_LANGUAGES)

ALLOWED_AUDIO_EXTENSIONS: frozenset[str] = frozenset(
    {".wav", ".mp3", ".m4a", ".ogg", ".webm"}
)

_DEFAULT_MAX_UPLOAD_BYTES = 25 * 1024 * 1024


def max_upload_bytes() -> int:
    raw = os.environ.get("MAX_UPLOAD_BYTES", str(_DEFAULT_MAX_UPLOAD_BYTES))
    return int(raw)


def service_api_key() -> str:
    return os.environ.get("SERVICE_API_KEY", "").strip()


_DEFAULT_CORS_ORIGINS = (
    "http://localhost:4321",
    "https://voice-translate-flax.vercel.app",
)


def cors_allow_origins() -> list[str]:
    raw = os.environ.get("CORS_ORIGINS", "").strip()
    if not raw:
        return list(_DEFAULT_CORS_ORIGINS)
    return [origin.strip() for origin in raw.split(",") if origin.strip()]
