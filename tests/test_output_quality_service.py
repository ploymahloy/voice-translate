from unittest.mock import patch

from tests.audio_helpers import (
    assert_duration_within_tolerance,
    assert_output_validity,
)
from tests.conftest import (
    FAKE_OUTPUT_AUDIO,
    FAKE_VOICE_PROFILE,
    one_second_wav_bytes,
)
from app.services.translate_service import run_translation

@patch("app.services.translate_service.translate_and_synthesize")
@patch("app.services.translate_service.extract_voice_profile")
def test_output_validity_non_zero_size_and_valid_audio_header(
    mock_extract, mock_translate
):
    mock_extract.return_value = FAKE_VOICE_PROFILE
    mock_translate.return_value = FAKE_OUTPUT_AUDIO

    output = run_translation(
        source_audio=one_second_wav_bytes(),
        filename="one_second.wav",
        target_language="es",
    )

    assert_output_validity(output)

@patch("app.services.translate_service.translate_and_synthesize")
@patch("app.services.translate_service.extract_voice_profile")
def test_output_duration_matches_input_within_tolerance(mock_extract, mock_translate):
    mock_extract.return_value = FAKE_VOICE_PROFILE
    mock_translate.return_value = FAKE_OUTPUT_AUDIO

    output = run_translation(
        source_audio=one_second_wav_bytes(),
        filename="one_second.wav",
        target_language="es",
    )

    assert_duration_within_tolerance(
        one_second_wav_bytes(),
        output,
        input_filename="one_second.wav",
    )
