import logging
import os
import tempfile
import time
import uuid
from pathlib import Path
from typing import Literal

import httpx

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.elevenlabs.io"
_REQUEST_TIMEOUT = 60.0
_POLL_INTERVAL_SEC = 2.0
_POLL_MAX_WAIT_SEC = 90.0

_VOICE_CLONE_AUTH_ERROR = "Elevenv3 Voice Clone API key invalid or expired"
_ELEVEN_API_AUTH_ERROR = "Eleven API key invalid or expired"
_VOICE_CLONE_TIMEOUT = "Voice Clone request timed out"
_ELEVEN_API_TIMEOUT = "Eleven API request timed out"

AuthContext = Literal["voice_clone", "eleven_api"]


class ElevenLabsClient:
    def __init__(
        self, base_url: str = _BASE_URL, timeout: float = _REQUEST_TIMEOUT
    ) -> None:
        self._base_url = base_url
        self._timeout = timeout

    def api_key(self) -> str:
        return os.environ.get("ELEVENV3_API_KEY", "").strip()

    def _headers(self) -> dict[str, str]:
        return {"xi-api-key": self.api_key()}

    def request(
        self,
        method: str,
        url: str,
        *,
        auth_context: AuthContext,
        **kwargs,
    ) -> httpx.Response:
        auth_error = (
            _ELEVEN_API_AUTH_ERROR
            if auth_context == "eleven_api"
            else _VOICE_CLONE_AUTH_ERROR
        )
        timeout_message = (
            _ELEVEN_API_TIMEOUT
            if auth_context == "eleven_api"
            else _VOICE_CLONE_TIMEOUT
        )
        try:
            with httpx.Client(base_url=self._base_url, timeout=self._timeout) as (
                client
            ):
                response = client.request(
                    method, url, headers=self._headers(), **kwargs
                )
                response.raise_for_status()
                return response
        except httpx.TimeoutException as exc:
            raise httpx.TimeoutException(timeout_message) from exc
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in (401, 403):
                raise RuntimeError(auth_error) from exc
            raise

    def require_api_key(self, *, auth_context: AuthContext) -> None:
        if not self.api_key():
            message = (
                _ELEVEN_API_AUTH_ERROR
                if auth_context == "eleven_api"
                else _VOICE_CLONE_AUTH_ERROR
            )
            raise RuntimeError(message)


_client = ElevenLabsClient()


def extract_voice_profile(audio_path: str) -> dict:
    _client.require_api_key(auth_context="voice_clone")

    name = f"voice-translate-{uuid.uuid4()}"
    with open(audio_path, "rb") as audio_file:
        response = _client.request(
            "POST",
            "/v1/voices/add",
            auth_context="voice_clone",
            data={"name": name},
            files={"files": (Path(audio_path).name, audio_file)},
        )

    voice_id = response.json().get("voice_id")
    if not voice_id:
        raise RuntimeError("Voice Clone response missing voice_id")

    return {"id": voice_id}


def _dub_audio(audio_path: str, target_language: str) -> bytes:
    _client.require_api_key(auth_context="eleven_api")

    with open(audio_path, "rb") as audio_file:
        create_response = _client.request(
            "POST",
            "/v1/dubbing",
            auth_context="eleven_api",
            data={"source_lang": "auto", "target_lang": target_language},
            files={"file": (Path(audio_path).name, audio_file)},
        )

    dubbing_id = create_response.json().get("dubbing_id")
    if not dubbing_id:
        raise RuntimeError("Dubbing response missing dubbing_id")

    deadline = time.monotonic() + _POLL_MAX_WAIT_SEC
    while time.monotonic() < deadline:
        status_response = _client.request(
            "GET", f"/v1/dubbing/{dubbing_id}", auth_context="eleven_api"
        )
        status = status_response.json().get("status")
        if status == "dubbed":
            break
        if status in ("failed", "error"):
            raise RuntimeError(f"Dubbing failed with status: {status}")
        time.sleep(_POLL_INTERVAL_SEC)
    else:
        raise httpx.TimeoutException(_ELEVEN_API_TIMEOUT)

    audio_response = _client.request(
        "GET",
        f"/v1/dubbing/{dubbing_id}/audio/{target_language}",
        auth_context="eleven_api",
    )
    return audio_response.content


_STS_MODEL_ID = "eleven_multilingual_sts_v2"
_STS_OUTPUT_FORMAT = "mp3_44100_128"


def _apply_cloned_voice(voice_id: str, dubbed_audio: bytes) -> bytes:
    _client.require_api_key(auth_context="eleven_api")

    fd, dubbed_path = tempfile.mkstemp(suffix=".mp3")
    try:
        with os.fdopen(fd, "wb") as dubbed_file:
            dubbed_file.write(dubbed_audio)
        with open(dubbed_path, "rb") as audio_file:
            response = _client.request(
                "POST",
                f"/v1/speech-to-speech/{voice_id}",
                auth_context="eleven_api",
                params={"output_format": _STS_OUTPUT_FORMAT},
                data={"model_id": _STS_MODEL_ID},
                files={
                    "audio": ("dubbed.mp3", audio_file, "audio/mpeg")
                },
            )
    finally:
        try:
            os.unlink(dubbed_path)
        except OSError:
            pass

    return response.content


def delete_voice_profile(profile: dict) -> None:
    voice_id = profile.get("id")
    if not voice_id or not _client.api_key():
        return
    try:
        _client.request(
            "DELETE",
            f"/v1/voices/{voice_id}",
            auth_context="voice_clone",
        )
    except (httpx.HTTPError, RuntimeError) as exc:
        logger.warning(
            "Failed to delete voice profile request_id=unknown voice_id=%s error=%s",
            voice_id,
            exc,
        )


def translate_and_synthesize(profile: dict, target_language: str, audio_path: str) -> bytes:
    voice_id = profile.get("id")
    if not voice_id:
        raise RuntimeError("Voice profile missing voice id")

    dubbed = _dub_audio(audio_path, target_language)
    return _apply_cloned_voice(voice_id, dubbed)

