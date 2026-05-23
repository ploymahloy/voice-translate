import io
import wave
from typing import Literal

from mutagen._file import File as MutagenFile

OutputFormat = Literal["mp3", "wav"]

EXPECTED_OUTPUT_MEDIA_TYPES = frozenset({"audio/mpeg", "audio/wav", "audio/wave"})


def is_valid_mp3(data: bytes) -> bool:
    if len(data) < 3:
        return False
    if data[:3] == b"ID3":
        return True
    if len(data) >= 2 and data[0] == 0xFF and (data[1] & 0xE0) == 0xE0:
        return True
    return False


def is_valid_wav(data: bytes) -> bool:
    return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WAVE"


def detect_output_format(data: bytes) -> OutputFormat | None:
    if is_valid_wav(data):
        return "wav"
    if is_valid_mp3(data):
        return "mp3"
    return None


def is_valid_output_audio(data: bytes) -> bool:
    return len(data) > 0 and detect_output_format(data) is not None


def _wav_duration_seconds(data: bytes) -> float:
    with wave.open(io.BytesIO(data), "rb") as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        if rate == 0:
            raise ValueError("WAV file has zero sample rate")
        return frames / rate


def _mp3_duration_seconds(data: bytes) -> float:
    audio = MutagenFile(io.BytesIO(data))
    if audio is None or audio.info is None or audio.info.length is None:
        raise ValueError("Unable to determine MP3 duration")
    return float(audio.info.length)


def audio_duration_seconds(data: bytes) -> float:
    fmt = detect_output_format(data)
    if fmt == "wav":
        return _wav_duration_seconds(data)
    if fmt == "mp3":
        return _mp3_duration_seconds(data)
    raise ValueError("Unrecognized audio format")


def assert_output_validity(data: bytes) -> None:
    assert len(data) > 0, "Output audio is empty"
    assert is_valid_output_audio(data), (
        "Output audio has no valid MP3 or WAV header"
    )


def assert_duration_within_tolerance(
    input_bytes: bytes,
    output_bytes: bytes,
    *,
    input_filename: str,
) -> None:
    _ = input_filename
    input_duration = _wav_duration_seconds(input_bytes)
    output_duration = audio_duration_seconds(output_bytes)
    tolerance = max(0.5, input_duration * 0.25)
    assert abs(output_duration - input_duration) <= tolerance, (
        f"Output duration {output_duration:.2f}s differs from input "
        f"{input_duration:.2f}s by more than {tolerance:.2f}s"
    )
