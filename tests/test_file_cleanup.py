from pathlib import Path
from unittest.mock import patch

import pytest

from tests.conftest import (
    FAKE_OUTPUT_AUDIO,
    FAKE_VOICE_PROFILE,
    VALID_SOURCE_BYTES,
    track_mkstemp,
)

from app.services.translate_service import run_translation


@patch("app.services.translate_service.translate_and_synthesize")
@patch("app.services.translate_service.extract_voice_profile")
def test_temp_files_removed_on_success(mock_extract, mock_translate):
    mock_extract.return_value = FAKE_VOICE_PROFILE
    mock_translate.return_value = FAKE_OUTPUT_AUDIO

    with track_mkstemp() as created:
        run_translation(
            source_audio=VALID_SOURCE_BYTES,
            filename="clip.wav",
            target_language="es",
        )

    for path in created:
        assert not Path(path).exists()


@patch("app.services.translate_service.translate_and_synthesize")
@patch("app.services.translate_service.extract_voice_profile")
def test_temp_files_removed_on_failure(mock_extract, mock_translate):
    mock_extract.return_value = FAKE_VOICE_PROFILE
    mock_translate.side_effect = RuntimeError("AI failed")

    with track_mkstemp() as created:
        with pytest.raises(RuntimeError, match="AI failed"):
            run_translation(
                source_audio=VALID_SOURCE_BYTES,
                filename="clip.wav",
                target_language="es",
            )

    for path in created:
        assert not Path(path).exists()
