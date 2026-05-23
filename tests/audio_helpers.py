from app.audio_quality import (
    OutputFormat,
    audio_duration_seconds,
    detect_output_format,
    is_valid_output_audio,
    wav_duration_seconds,
)

EXPECTED_OUTPUT_MEDIA_TYPES = frozenset({"audio/mp3", "audio/wav"})


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
    input_duration = wav_duration_seconds(input_bytes)
    output_duration = audio_duration_seconds(output_bytes)
    tolerance = max(0.5, input_duration * 0.25)
    assert abs(output_duration - input_duration) <= tolerance, (
        f"Output duration {output_duration:.2f}s differs from input "
        f"{input_duration:.2f}s by more than {tolerance:.2f}s"
    )


__all__ = [
    "EXPECTED_OUTPUT_MEDIA_TYPES",
    "OutputFormat",
    "assert_duration_within_tolerance",
    "assert_output_validity",
    "detect_output_format",
]
