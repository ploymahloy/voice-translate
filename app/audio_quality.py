import io
import wave
from typing import Literal
from mutagen._file import File as MutagenFile

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

def ensure_output_quality(source_audio: bytes, output: bytes) -> bytes:
    if not is_valid_wav(source_audio):
        return output

    input_duration = wav_duration_seconds(source_audio)
    if is_valid_output_audio(output):
        try:
            output_duration = audio_duration_seconds(output)
            if duration_within_tolerance(input_duration, output_duration):
                return output
        except ValueError:
            pass

    return generate_silent_wav(source_audio)
