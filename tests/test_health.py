from tests.conftest import (
    FAKE_VOICE_PROFILE,
    patch_extract_voice_profile,
    patch_translate_and_synthesize,
    post_translate_one_second_wav,
    valid_output_wav_bytes,
)

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "voice-translate"
    assert body["health"] == "/health"

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_ready_without_api_key(client, monkeypatch):
    monkeypatch.delenv("ELEVENV3_API_KEY", raising=False)
    response = client.get("/ready")
    assert response.status_code == 503

def test_ready_with_api_key(client, monkeypatch):
    monkeypatch.setenv("ELEVENV3_API_KEY", "test-key")
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}

def test_translate_returns_request_id_header(client):
    with patch_extract_voice_profile(return_value=FAKE_VOICE_PROFILE):
        with patch_translate_and_synthesize(return_value=valid_output_wav_bytes()):
            response = post_translate_one_second_wav(client)

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")

def test_invalid_output_returns_502(client):
    with patch_extract_voice_profile(return_value=FAKE_VOICE_PROFILE):
        with patch_translate_and_synthesize(return_value=b"invalid-output"):
            response = post_translate_one_second_wav(client)

    assert response.status_code == 502
    assert "not valid audio" in response.json()["detail"].lower()
