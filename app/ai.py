import os
import tempfile
import time
import uuid
from pathlib import Path
import httpx

_BASE_URL = "https://api.elevenlabs.io"
_REQUEST_TIMEOUT = 60.0
_POLL_INTERVAL_SEC = 2.0
_POLL_MAX_WAIT_SEC = 90.0

_VOICE_CLONE_AUTH_ERROR = "Elevenv3 Voice Clone API key invalid or expired"
_ELEVEN_API_AUTH_ERROR = "Eleven API key invalid or expired"
_VOICE_CLONE_TIMEOUT = "Voice Clone request timed out"
_ELEVEN_API_TIMEOUT = "Eleven API request timed out"

def _api_key() -> str:
    return os.environ.get("ELEVENV3_API_KEY", "").strip()

def _headers() -> dict[str, str]:
    return {"xi-api-key": _api_key()}

def _map_auth_error(exc: httpx.HTTPStatusError, *, eleven_api: bool) -> RuntimeError:
    message = _ELEVEN_API_AUTH_ERROR if eleven_api else _VOICE_CLONE_AUTH_ERROR
    return RuntimeError(message)

def _voice_clone_request(
    method: str, url: str, **kwargs
) -> httpx.Response:
    try:
        with httpx.Client(
            base_url=_BASE_URL, timeout=_REQUEST_TIMEOUT
        ) as client:
            response = client.request(method, url, headers=_headers(), **kwargs)
            response.raise_for_status()
            return response
    except httpx.TimeoutException as exc:
        raise httpx.TimeoutException(_VOICE_CLONE_TIMEOUT) from exc
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code in (401, 403):
            raise _map_auth_error(exc, eleven_api=False) from exc
        raise

def _eleven_request(method: str, url: str, **kwargs) -> httpx.Response:
    try:
        with httpx.Client(
            base_url=_BASE_URL, timeout=_REQUEST_TIMEOUT
        ) as client:
            response = client.request(method, url, headers=_headers(), **kwargs)
            response.raise_for_status()
            return response
    except httpx.TimeoutException as exc:
        raise httpx.TimeoutException(_ELEVEN_API_TIMEOUT) from exc
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code in (401, 403):
            raise _map_auth_error(exc, eleven_api=True) from exc
        raise

def extract_voice_profile(audio_path: str) -> dict:
    if not _api_key():
        raise RuntimeError(_VOICE_CLONE_AUTH_ERROR)

    name = f"voice-translate-{uuid.uuid4()}"
    with open(audio_path, "rb") as audio_file:
        response = _voice_clone_request(
            "POST",
            "/v1/voices/add",
            data={"name": name},
            files={"files": (Path(audio_path).name, audio_file)},
        )

    voice_id = response.json().get("voice_id")
    if not voice_id:
        raise RuntimeError("Voice Clone response missing voice_id")

    return {"id": voice_id}


def _dub_audio(audio_path: str, target_language: str) -> bytes:
    if not _api_key():
        raise RuntimeError(_ELEVEN_API_AUTH_ERROR)

    with open(audio_path, "rb") as audio_file:
        create_response = _eleven_request(
            "POST",
            "/v1/dubbing",
            data={"source_lang": "auto", "target_lang": target_language},
            files={"file": (Path(audio_path).name, audio_file)},
        )

    dubbing_id = create_response.json().get("dubbing_id")
    if not dubbing_id:
        raise RuntimeError("Dubbing response missing dubbing_id")

    deadline = time.monotonic() + _POLL_MAX_WAIT_SEC
    while time.monotonic() < deadline:
        status_response = _eleven_request("GET", f"/v1/dubbing/{dubbing_id}")
        status = status_response.json().get("status")
        if status == "dubbed":
            break
        if status in ("failed", "error"):
            raise RuntimeError(f"Dubbing failed with status: {status}")
        time.sleep(_POLL_INTERVAL_SEC)
    else:
        raise httpx.TimeoutException(_ELEVEN_API_TIMEOUT)

    audio_response = _eleven_request(
        "GET", f"/v1/dubbing/{dubbing_id}/audio/{target_language}"
    )
    return audio_response.content


_STS_MODEL_ID = "eleven_multilingual_sts_v2"
_STS_OUTPUT_FORMAT = "mp3_44100_128"


def _apply_cloned_voice(voice_id: str, dubbed_audio: bytes) -> bytes:
    if not _api_key():
        raise RuntimeError(_ELEVEN_API_AUTH_ERROR)

    fd, dubbed_path = tempfile.mkstemp(suffix=".mp3")
    try:
        with os.fdopen(fd, "wb") as dubbed_file:
            dubbed_file.write(dubbed_audio)
        with open(dubbed_path, "rb") as audio_file:
            response = _eleven_request(
                "POST",
                f"/v1/speech-to-speech/{voice_id}",
                params={"output_format": _STS_OUTPUT_FORMAT},
                data={"model_id": _STS_MODEL_ID},
                files={"audio": ("dubbed.mp3", audio_file, "audio/mpeg")},
            )
    finally:
        try:
            os.unlink(dubbed_path)
        except OSError:
            pass

    return response.content


def delete_voice_profile(profile: dict) -> None:
    voice_id = profile.get("id")
    if not voice_id or not _api_key():
        return
    try:
        _voice_clone_request("DELETE", f"/v1/voices/{voice_id}")
    except (httpx.HTTPError, RuntimeError):
        pass


def translate_and_synthesize(
    profile: dict, target_language: str, audio_path: str
) -> bytes:
    voice_id = profile.get("id")
    if not voice_id:
        raise RuntimeError("Voice profile missing voice id")

    dubbed = _dub_audio(audio_path, target_language)
    return _apply_cloned_voice(voice_id, dubbed)
