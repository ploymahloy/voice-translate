from tests.audio_helpers import (
    EXPECTED_OUTPUT_MEDIA_TYPES,
    assert_duration_within_tolerance,
    assert_output_validity,
)
from tests.conftest import (
    FAKE_OUTPUT_AUDIO,
    FAKE_VOICE_PROFILE,
    one_second_wav_bytes,
    patch_extract_voice_profile,
    patch_translate_and_synthesize,
    post_translate_one_second_wav,
)

def test_output_validity_non_zero_size_and_valid_audio_header(client):
    with patch_extract_voice_profile(return_value=FAKE_VOICE_PROFILE):
        with patch_translate_and_synthesize(return_value=FAKE_OUTPUT_AUDIO):
            response = post_translate_one_second_wav(client)

    assert response.status_code == 200
    content_type = response.headers.get("content-type", "").split(";")[0].strip()
    assert content_type in EXPECTED_OUTPUT_MEDIA_TYPES
    assert_output_validity(response.content)

def test_output_duration_matches_input_within_tolerance(client):
    with patch_extract_voice_profile(return_value=FAKE_VOICE_PROFILE):
        with patch_translate_and_synthesize(return_value=FAKE_OUTPUT_AUDIO):
            response = post_translate_one_second_wav(client)

    assert response.status_code == 200
    assert_duration_within_tolerance(
        one_second_wav_bytes(),
        response.content,
        input_filename="one_second.wav",
    )
