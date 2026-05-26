import io
import os
import tempfile
import wave
from collections.abc import Generator, Mapping
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.audio_helpers import assert_output_validity

SUCCESS_AUDIO_MEDIA_TYPES = frozenset({"audio/mp3", "audio/wav"})

TRANSLATE_URL = "/translate"
VALID_TARGET_LANGUAGE = "es"
SUPPORTED_LANGUAGES = ("en", "es", "fr", "de")

FAKE_VOICE_PROFILE = {"id": "test-profile"}
VALID_SOURCE_BYTES = b"\x00\x01\x02"

FIXTURES_DIR = Path(__file__).parent / "fixtures"
ONE_SECOND_WAV = FIXTURES_DIR / "one_second.wav"

VOICE_CLONE_UPSTREAM_FAILURES = (
    RuntimeError("Elevenv3 Voice Clone API key invalid or expired"),
    httpx.TimeoutException("Voice Clone request timed out"),
)

ELEVEN_API_UPSTREAM_FAILURES = (
    RuntimeError("Eleven API key invalid or expired"),
    httpx.TimeoutException("Eleven API request timed out"),
)

def valid_output_wav_bytes() -> bytes:
    """Valid WAV output matching one_second_wav duration for quality checks."""
    return one_second_wav_bytes()

@pytest.fixture(autouse=True)
def _clear_service_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SERVICE_API_KEY", raising=False)

@contextmanager
def track_mkstemp() -> Generator[list[str], None, None]:
    created: list[str] = []
    real_mkstemp = tempfile.mkstemp

    def recording_mkstemp(*args, **kwargs):
        fd, path = real_mkstemp(*args, **kwargs)
        created.append(path)
        return fd, path

    with patch(
        "app.services.translate_service.tempfile.mkstemp",
        side_effect=recording_mkstemp,
    ):
        yield created

@pytest.fixture
def client() -> TestClient:
    return TestClient(app)

def response_detail_text(response) -> str:
    body = response.json()
    detail = body.get("detail", "")
    if isinstance(detail, list):
        return " ".join(str(item) for item in detail)
    return str(detail)

def post_translate(
    client: TestClient,
    *,
    target_language: str | None = None,
    files: Mapping[str, tuple] | None = None,
    data: Mapping[str, str] | None = None,
    headers: Mapping[str, str] | None = None,
):
    form_data = dict(data or {})
    if target_language is not None:
        form_data["target_language"] = target_language
    return client.post(
        TRANSLATE_URL, data=form_data, files=files, headers=dict(headers or {})
    )

def audio_file(filename: str, content: bytes, content_type: str) -> dict:
    return {"source_audio": (filename, io.BytesIO(content), content_type)}

def write_wav_fixture(path: Path, duration_seconds: float, *, rate: int = 16000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    nframes = int(rate * duration_seconds)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(rate)
        wav_file.writeframes(b"\x00\x00" * nframes)

def _write_one_second_wav(path: Path) -> None:
    write_wav_fixture(path, 1.0)

def wav_bytes_for_duration(duration_seconds: float, *, rate: int = 16000) -> bytes:
    buffer = io.BytesIO()
    nframes = int(rate * duration_seconds)
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(rate)
        wav_file.writeframes(b"\x00\x00" * nframes)
    return buffer.getvalue()

def one_second_wav_bytes() -> bytes:
    if not ONE_SECOND_WAV.is_file():
        _write_one_second_wav(ONE_SECOND_WAV)
    return ONE_SECOND_WAV.read_bytes()

def one_second_wav_upload() -> dict:
    return audio_file("one_second.wav", one_second_wav_bytes(), "audio/wav")

def post_translate_one_second_wav(
    client: TestClient,
    *,
    target_language: str = VALID_TARGET_LANGUAGE,
    headers: Mapping[str, str] | None = None,
):
    return post_translate(
        client,
        target_language=target_language,
        files=one_second_wav_upload(),
        headers=headers,
    )

@contextmanager
def patch_extract_voice_profile(
    side_effect=None, *, return_value=None
) -> Generator[None, None, None]:
    patch_kwargs: dict = {}
    if side_effect is not None:
        patch_kwargs["side_effect"] = side_effect
    if return_value is not None:
        patch_kwargs["return_value"] = return_value
    with patch(
        "app.services.translate_service.extract_voice_profile",
        **patch_kwargs,
    ):
        yield

@contextmanager
def patch_translate_and_synthesize(
    side_effect=None, *, return_value=None
) -> Generator[None, None, None]:
    patch_kwargs: dict = {}
    if side_effect is not None:
        patch_kwargs["side_effect"] = side_effect
    if return_value is not None:
        patch_kwargs["return_value"] = return_value
    with patch(
        "app.services.translate_service.translate_and_synthesize",
        **patch_kwargs,
    ):
        yield

def assert_upstream_error_response(response) -> None:
    assert response.status_code in (500, 503)
    content_type = response.headers.get("content-type", "").split(";")[0].strip()
    assert content_type not in SUCCESS_AUDIO_MEDIA_TYPES

def assert_valid_audio_response(response, *, min_bytes: int = 100) -> None:
    assert response.status_code == 200
    content_type = response.headers.get("content-type", "").split(";")[0].strip()
    assert content_type in SUCCESS_AUDIO_MEDIA_TYPES
    assert_output_validity(response.content)
    assert len(response.content) >= min_bytes

def skip_without_elevenv3_key() -> None:
    if not os.environ.get("ELEVENV3_API_KEY", "").strip():
        pytest.skip("ELEVENV3_API_KEY not set")
