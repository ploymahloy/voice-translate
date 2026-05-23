import pytest

from tests.conftest import (
    SUPPORTED_LANGUAGES,
    VALID_TARGET_LANGUAGE,
    audio_file,
    post_translate,
    response_detail_text,
)

def test_missing_source_audio_file(client):
    response = post_translate(client, target_language=VALID_TARGET_LANGUAGE)

    assert response.status_code == 400
    assert "Missing source audio file" in response_detail_text(response)

@pytest.mark.parametrize(
    "filename,content,content_type",
    [
        ("notes.txt", b"hello", "text/plain"),
        ("clip.flac", b"\x00\x01\x02", "audio/flac"),
    ],
)
def test_unsupported_file_format(client, filename, content, content_type):
    response = post_translate(
        client,
        target_language=VALID_TARGET_LANGUAGE,
        files=audio_file(filename, content, content_type),
    )

    assert response.status_code == 415
    detail = response_detail_text(response).lower()
    assert "unsupported" in detail or "format" in detail

@pytest.mark.parametrize("target_language", ["Elvish", ""])
def test_invalid_target_language(client, target_language):
    response = post_translate(
        client,
        target_language=target_language,
        files=audio_file("clip.wav", b"\x00\x01", "audio/wav"),
    )

    assert response.status_code == 422
    detail = response_detail_text(response).lower()
    assert "supported" in detail or all(lang in detail for lang in SUPPORTED_LANGUAGES)

def test_empty_audio_file(client):
    response = post_translate(
        client,
        target_language=VALID_TARGET_LANGUAGE,
        files=audio_file("empty.wav", b"", "audio/wav"),
    )

    assert response.status_code == 400
    detail = response_detail_text(response).lower()
    assert "empty" in detail or "zero" in detail
