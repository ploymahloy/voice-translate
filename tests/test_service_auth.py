from tests.conftest import (
    FAKE_VOICE_PROFILE,
    patch_extract_voice_profile,
    patch_translate_and_synthesize,
    post_translate_one_second_wav,
    valid_output_wav_bytes,
)

def test_translate_requires_api_key_when_configured(client, monkeypatch):
    monkeypatch.setenv("SERVICE_API_KEY", "secret-key")
    response = post_translate_one_second_wav(client)
    assert response.status_code == 401

def test_translate_accepts_matching_api_key(client, monkeypatch):
    monkeypatch.setenv("SERVICE_API_KEY", "secret-key")
    with patch_extract_voice_profile(return_value=FAKE_VOICE_PROFILE):
        with patch_translate_and_synthesize(return_value=valid_output_wav_bytes()):
            response = post_translate_one_second_wav(
                client, headers={"X-API-Key": "secret-key"}
            )

    assert response.status_code == 200

def test_upload_exceeding_max_size_returns_413(client, monkeypatch):
    monkeypatch.setenv("MAX_UPLOAD_BYTES", "10")
    response = post_translate_one_second_wav(client)
    assert response.status_code == 413
