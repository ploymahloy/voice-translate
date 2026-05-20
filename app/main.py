from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from app.dependencies import ALLOWED_AUDIO_EXTENSIONS, SUPPORTED_LANGUAGES

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

    return {"status": "accepted"}
