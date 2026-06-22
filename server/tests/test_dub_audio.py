from unittest.mock import MagicMock, mock_open, patch

from server.ai import _dub_audio


def _json_response(payload: dict) -> MagicMock:
    response = MagicMock()
    response.json.return_value = payload
    return response


@patch("builtins.open", mock_open(read_data=b"audio"))
@patch("server.ai._client.request")
def test_dub_audio_uses_iso639_1_for_elevenlabs(mock_request):
    mock_request.side_effect = [
        _json_response({"dubbing_id": "dub-123"}),
        _json_response({"status": "dubbed"}),
        MagicMock(content=b"dubbed-audio"),
    ]

    result = _dub_audio("/tmp/input.wav", "spa")

    assert result == b"dubbed-audio"
    create_call = mock_request.call_args_list[0]
    assert create_call.args == ("POST", "/v1/dubbing")
    assert create_call.kwargs["data"]["target_lang"] == "es"

    audio_call = mock_request.call_args_list[2]
    assert audio_call.args == ("GET", "/v1/dubbing/dub-123/audio/es")
