import pytest

from tests.conftest import (
    UPSTREAM_FAILURES,
    assert_audio_mpeg_response,
    assert_upstream_error_response,
    patch_extract_voice_profile,
    post_translate_one_second_wav,
)


@pytest.mark.parametrize("side_effect", UPSTREAM_FAILURES)
def test_upstream_failure_returns_5xx(client, side_effect):
    with patch_extract_voice_profile(side_effect):
        response = post_translate_one_second_wav(client)
    assert_upstream_error_response(response)


@pytest.mark.integration
def test_translate_happy_path_real_gemini(client):
    response = post_translate_one_second_wav(client)
    assert_audio_mpeg_response(response)
