import os
import tempfile
from pathlib import Path

from app.ai import (
    delete_voice_profile,
    extract_voice_profile,
    translate_and_synthesize,
)
from app.audio_quality import ensure_output_quality

def run_translation(
    *,
    source_audio: bytes,
    filename: str,
    target_language: str,
) -> bytes:
    fd, input_path = tempfile.mkstemp(suffix=Path(filename).suffix)
    paths_to_clean = [input_path]
    profile: dict | None = None
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(source_audio)
        profile = extract_voice_profile(input_path)
        raw_output = translate_and_synthesize(profile, target_language, input_path)
        return ensure_output_quality(source_audio, raw_output)
    finally:
        if profile is not None:
            delete_voice_profile(profile)
        for path in paths_to_clean:
            try:
                os.unlink(path)
            except OSError:
                pass
