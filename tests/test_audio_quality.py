import pytest

from app.audio_quality import (
    OutputQualityError,
    audio_duration_seconds,
    detect_output_format,
    duration_within_tolerance,
    ensure_output_quality,
    is_valid_mp3,
    is_valid_wav,
)
from tests.conftest import one_second_wav_bytes, wav_bytes_for_duration

def test_is_valid_wav_and_mp3_headers():
    assert is_valid_wav(one_second_wav_bytes())
    assert not is_valid_mp3(one_second_wav_bytes())
    assert is_valid_mp3(b"ID3" + b"\x00" * 10)
    assert not is_valid_wav(b"not-a-wav")

def test_detect_output_format():
    assert detect_output_format(one_second_wav_bytes()) == "wav"
    assert detect_output_format(b"ID3\x00") == "mp3"
    assert detect_output_format(b"garbage") is None

def test_duration_within_tolerance():
    assert duration_within_tolerance(1.0, 1.2)
    assert not duration_within_tolerance(1.0, 2.0)

def test_ensure_output_quality_accepts_matching_wav():
    source = one_second_wav_bytes()
    result = ensure_output_quality(source, source)
    assert result == source

def test_ensure_output_quality_rejects_invalid_output():
    with pytest.raises(OutputQualityError, match="not valid audio"):
        ensure_output_quality(one_second_wav_bytes(), b"bad-output")

def test_ensure_output_quality_rejects_duration_mismatch():
    short = wav_bytes_for_duration(0.2)
    with pytest.raises(OutputQualityError, match="differs from input"):
        ensure_output_quality(one_second_wav_bytes(), short)

def test_audio_duration_seconds_wav():
    assert audio_duration_seconds(one_second_wav_bytes()) == pytest.approx(1.0, abs=0.01)
