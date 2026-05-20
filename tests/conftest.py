import io
from collections.abc import Mapping

import pytest
from fastapi.testclient import TestClient

from main import app

TRANSLATE_URL = "/translate"
VALID_TARGET_LANGUAGE = "es"
SUPPORTED_LANGUAGES = ("en", "es", "fr", "de")


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
