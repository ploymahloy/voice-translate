from pathlib import Path
from typing import Annotated

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from app.dependencies import ALLOWED_AUDIO_EXTENSIONS, SUPPORTED_LANGUAGES
from app.audio_quality import detect_output_format, media_type_for_format
from app.services.translate_service import run_translation

app = FastAPI()


@app.post("/translate")
async def translate(
    target_language: Annotated[str | None, Form()] = None,
    source_audio: Annotated[UploadFile | None, File()] = None,
):
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

    suffix = Path(source_audio.filename).suffix.lower()
    if suffix not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Unsupported audio format")

    try:
        audio_bytes = run_translation(
            source_audio=content,
            filename=source_audio.filename,
            target_language=target_language,
        )
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Translation failed") from exc

    fmt = detect_output_format(audio_bytes) or "mp3"
    return Response(content=audio_bytes, media_type=media_type_for_format(fmt))
