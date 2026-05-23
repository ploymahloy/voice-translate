import pytest

from tests.conftest import (
    ELEVEN_API_UPSTREAM_FAILURES,
    FAKE_VOICE_PROFILE,
    VOICE_CLONE_UPSTREAM_FAILURES,
    assert_valid_audio_response,
    assert_upstream_error_response,
    patch_extract_voice_profile,
    patch_translate_and_synthesize,
    post_translate_one_second_wav,
    skip_without_elevenv3_key,
)


@pytest.mark.parametrize("side_effect", VOICE_CLONE_UPSTREAM_FAILURES)
def test_voice_clone_upstream_failure_returns_5xx(client, side_effect):
    with patch_extract_voice_profile(side_effect):
        response = post_translate_one_second_wav(client)
    assert_upstream_error_response(response)


@pytest.mark.parametrize("side_effect", ELEVEN_API_UPSTREAM_FAILURES)
def test_eleven_api_upstream_failure_returns_5xx(client, side_effect):
    with patch_extract_voice_profile(return_value=FAKE_VOICE_PROFILE):
        with patch_translate_and_synthesize(side_effect):
            response = post_translate_one_second_wav(client)
    assert_upstream_error_response(response)


@pytest.mark.integration
def test_translate_happy_path_real_elevenlabs(client):
    skip_without_elevenv3_key()
    response = post_translate_one_second_wav(client)
    assert_valid_audio_response(response)
