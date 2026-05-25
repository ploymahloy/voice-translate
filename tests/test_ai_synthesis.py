from unittest.mock import patch

from app.ai import translate_and_synthesize

FAKE_PROFILE = {"id": "cloned-voice-id"}
FAKE_DUBBED = b"fake-dubbed-audio"
FAKE_CLONED = b"fake-cloned-output"


@patch("app.ai._apply_cloned_voice", return_value=FAKE_CLONED)
@patch("app.ai._dub_audio", return_value=FAKE_DUBBED)
def test_translate_and_synthesize_dubs_then_applies_clone(
    mock_dub, mock_apply
):
    result = translate_and_synthesize(FAKE_PROFILE, "es", "/tmp/input.wav")

    mock_dub.assert_called_once_with("/tmp/input.wav", "es")
    mock_apply.assert_called_once_with("cloned-voice-id", FAKE_DUBBED)
    assert result == FAKE_CLONED


@patch("app.ai._dub_audio")
def test_translate_and_synthesize_requires_voice_id(mock_dub):
    try:
        translate_and_synthesize({}, "es", "/tmp/input.wav")
    except RuntimeError as exc:
        assert "missing voice id" in str(exc).lower()
    else:
        raise AssertionError("expected RuntimeError")
    mock_dub.assert_not_called()
