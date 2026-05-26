import asyncio
import logging
from pathlib import Path
from typing import Annotated

import httpx
from fastapi import FastAPI, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.responses import Response

from app.config import (
    ALLOWED_AUDIO_EXTENSIONS,
    SUPPORTED_LANGUAGES,
    max_upload_bytes,
    service_api_key,
)
from app.env import load_env_file
from app.exceptions import OutputQualityError
from app.audio_quality import detect_output_format, media_type_for_format
from app.logging_config import configure_logging
from app.middleware import REQUEST_ID_HEADER, RequestContextMiddleware
from app.services.translate_service import run_translation

load_env_file()
configure_logging()

logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(RequestContextMiddleware)

def _require_service_api_key(api_key: str | None) -> None:
    expected = service_api_key()
    if not expected:
        return
    if api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

@app.get("/")
def root():
    return {
        "service": "voice-translate",
        "docs": "/docs",
        "translate": "POST /translate",
        "health": "/health",
        "ready": "/ready",
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    import os

    if not os.environ.get("ELEVENV3_API_KEY", "").strip():
        raise HTTPException(
            status_code=503,
            detail="ELEVENV3_API_KEY is not configured",
        )
    return {"status": "ready"}

@app.post("/translate")
async def translate(
    request: Request,
    target_language: Annotated[str | None, Form()] = None,
    source_audio: Annotated[UploadFile | None, File()] = None,
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
):
    request_id = getattr(request.state, "request_id", "unknown")
    _require_service_api_key(x_api_key)

    if source_audio is None or not source_audio.filename:
        raise HTTPException(status_code=400, detail="Missing source audio file")

    if target_language is None or target_language not in SUPPORTED_LANGUAGES:
        supported = ", ".join(sorted(SUPPORTED_LANGUAGES))
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported target language. Supported: {supported}",
        )

    content = await source_audio.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Audio file is empty")

    limit = max_upload_bytes()
    if len(content) > limit:
        raise HTTPException(
            status_code=413,
            detail=f"Audio file exceeds maximum size of {limit} bytes",
        )

    suffix = Path(source_audio.filename).suffix.lower()
    if suffix not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Unsupported audio format")

    logger.info(
        "translation_started request_id=%s target_language=%s bytes=%s",
        request_id,
        target_language,
        len(content),
    )

    try:
        audio_bytes = await asyncio.to_thread(
            run_translation,
            source_audio=content,
            filename=source_audio.filename,
            target_language=target_language,
        )
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except OutputQualityError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception(
            "translation_failed request_id=%s error=%s", request_id, exc
        )
        raise HTTPException(status_code=500, detail="Translation failed") from exc

    fmt = detect_output_format(audio_bytes) or "mp3"
    logger.info(
        "translation_completed request_id=%s format=%s bytes=%s",
        request_id,
        fmt,
        len(audio_bytes),
    )
    response = Response(content=audio_bytes, media_type=media_type_for_format(fmt))
    response.headers[REQUEST_ID_HEADER] = request_id
    return response
