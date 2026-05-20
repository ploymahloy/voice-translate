import io
import os
import tempfile
from collections.abc import Generator, Mapping
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")

import pytest
from fastapi.testclient import TestClient

from app.main import app

TRANSLATE_URL = "/translate"
VALID_TARGET_LANGUAGE = "es"
SUPPORTED_LANGUAGES = ("en", "es", "fr", "de")

FAKE_VOICE_PROFILE = {"id": "test-profile"}
FAKE_OUTPUT_AUDIO = b"fake-output-audio-bytes"
VALID_SOURCE_BYTES = b"\x00\x01\x02"


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
):
    form_data = dict(data or {})
    if target_language is not None:
        form_data["target_language"] = target_language
    return client.post(TRANSLATE_URL, data=form_data, files=files)


def audio_file(filename: str, content: bytes, content_type: str) -> dict:
    return {"source_audio": (filename, io.BytesIO(content), content_type)}
