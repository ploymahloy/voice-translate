from pathlib import Path
from unittest.mock import patch

from tests.conftest import (
    FAKE_VOICE_PROFILE,
    one_second_wav_bytes,
    valid_output_wav_bytes,
)
from app.services.translate_service import run_translation

@patch("app.services.translate_service.translate_and_synthesize")
@patch("app.services.translate_service.extract_voice_profile")
def test_successful_orchestration(mock_extract, mock_translate):
    source = one_second_wav_bytes()
    output = valid_output_wav_bytes()

    def extract_with_existing_file(path):
        assert Path(path).exists()
        return FAKE_VOICE_PROFILE

    mock_extract.side_effect = extract_with_existing_file
    mock_translate.return_value = output

    result = run_translation(
        source_audio=source,
        filename="clip.wav",
        target_language="es",
    )

    mock_extract.assert_called_once()
    extract_path = mock_extract.call_args[0][0]

    mock_translate.assert_called_once_with(
        FAKE_VOICE_PROFILE, "es", extract_path
    )
    assert result == output
