import os
import tempfile
from pathlib import Path

from app.ai import extract_voice_profile, translate_and_synthesize


def run_translation(
    *,
    source_audio: bytes,
    filename: str,
    target_language: str,
) -> bytes:
    fd, input_path = tempfile.mkstemp(suffix=Path(filename).suffix)
    paths_to_clean = [input_path]
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(source_audio)
        profile = extract_voice_profile(input_path)
        return translate_and_synthesize(profile, target_language, input_path)
    finally:
        for path in paths_to_clean:
            try:
                os.unlink(path)
            except OSError:
                pass
