from pathlib import Path
from unittest.mock import patch

from tests.conftest import (
    FAKE_OUTPUT_AUDIO,
    FAKE_VOICE_PROFILE,
    VALID_SOURCE_BYTES,
)

from app.services.translate_service import run_translation


@patch("app.services.translate_service.translate_and_synthesize")
@patch("app.services.translate_service.extract_voice_profile")
def test_successful_orchestration(mock_extract, mock_translate):
    def extract_with_existing_file(path):
        assert Path(path).exists()
        return FAKE_VOICE_PROFILE

    mock_extract.side_effect = extract_with_existing_file
    mock_translate.return_value = FAKE_OUTPUT_AUDIO

    result = run_translation(
        source_audio=VALID_SOURCE_BYTES,
        filename="clip.wav",
        target_language="es",
    )

    mock_extract.assert_called_once()
    extract_path = mock_extract.call_args[0][0]

    mock_translate.assert_called_once_with(
        FAKE_VOICE_PROFILE, "es", extract_path
    )
    assert result == FAKE_OUTPUT_AUDIO
