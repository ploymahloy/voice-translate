import io
import wave
from typing import Literal

from mutagen._file import File as MutagenFile

from app.exceptions import OutputQualityError

OutputFormat = Literal["mp3", "wav"]

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

def wav_duration_seconds(data: bytes) -> float:
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
        return wav_duration_seconds(data)
    if fmt == "mp3":
        return _mp3_duration_seconds(data)
    raise ValueError("Unrecognized audio format")

def duration_within_tolerance(input_duration: float, output_duration: float) -> bool:
    tolerance = max(0.5, input_duration * 0.25)
    return abs(output_duration - input_duration) <= tolerance

def generate_silent_wav(source_audio: bytes) -> bytes:
    """Build silent WAV matching source layout (used in unit tests)."""
    with wave.open(io.BytesIO(source_audio), "rb") as source_wav:
        nchannels = source_wav.getnchannels()
        sampwidth = source_wav.getsampwidth()
        framerate = source_wav.getframerate()
        nframes = source_wav.getnframes()

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as output_wav:
        output_wav.setnchannels(nchannels)
        output_wav.setsampwidth(sampwidth)
        output_wav.setframerate(framerate)
        output_wav.writeframes(b"\x00" * (nframes * nchannels * sampwidth))
    return buffer.getvalue()

def media_type_for_format(fmt: OutputFormat) -> str:
    return "audio/wav" if fmt == "wav" else "audio/mp3"

def _source_duration_seconds(source_audio: bytes) -> float | None:
    try:
        return audio_duration_seconds(source_audio)
    except ValueError:
        return None

def ensure_output_quality(source_audio: bytes, output: bytes) -> bytes:
    if not is_valid_output_audio(output):
        raise OutputQualityError("Translation output is not valid audio")

    source_duration = _source_duration_seconds(source_audio)
    if source_duration is None:
        return output

    try:
        output_duration = audio_duration_seconds(output)
    except ValueError as exc:
        raise OutputQualityError(
            "Unable to determine translation output duration"
        ) from exc

    if not duration_within_tolerance(source_duration, output_duration):
        raise OutputQualityError(
            f"Output duration {output_duration:.2f}s differs from input "
            f"{source_duration:.2f}s by more than allowed tolerance"
        )

    return output
