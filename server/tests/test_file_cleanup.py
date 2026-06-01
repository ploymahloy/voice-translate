import pytest
from pathlib import Path

from unittest.mock import patch
from tests.conftest import (
    FAKE_VOICE_PROFILE,
    one_second_wav_bytes,
    valid_output_wav_bytes,
    track_mkstemp,
)
from server.services.translate_service import run_translation

@patch("server.services.translate_service.translate_and_synthesize")
@patch("server.services.translate_service.extract_voice_profile")
def test_temp_files_removed_on_success(mock_extract, mock_translate):
    mock_extract.return_value = FAKE_VOICE_PROFILE
    mock_translate.return_value = valid_output_wav_bytes()
    source = one_second_wav_bytes()

    with track_mkstemp() as created:
        run_translation(
            source_audio=source,
            filename="clip.wav",
            target_language="spa",
        )

    for path in created:
        assert not Path(path).exists()

@patch("server.services.translate_service.translate_and_synthesize")
@patch("server.services.translate_service.extract_voice_profile")
def test_temp_files_removed_on_failure(mock_extract, mock_translate):
    mock_extract.return_value = FAKE_VOICE_PROFILE
    mock_translate.side_effect = RuntimeError("AI failed")
    source = one_second_wav_bytes()

    with track_mkstemp() as created:
        with pytest.raises(RuntimeError, match="AI failed"):
            run_translation(
                source_audio=source,
                filename="clip.wav",
                target_language="spa",
            )

    for path in created:
        assert not Path(path).exists()
