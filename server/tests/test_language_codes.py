import pytest

from server.config import SUPPORTED_LANGUAGES
from server.language_codes import (
    assert_supported_languages_mapped,
    elevenlabs_dubbing_language_code,
)


@pytest.mark.parametrize(
    ("iso639_3", "expected"),
    [
        ("spa", "es"),
        ("eng", "en"),
        ("deu", "de"),
        ("zho", "zh"),
        ("tgl", "tl"),
    ],
)
def test_elevenlabs_dubbing_language_code_maps_iso639_1(iso639_3, expected):
    assert elevenlabs_dubbing_language_code(iso639_3) == expected


def test_elevenlabs_dubbing_language_code_falls_back_to_iso639_3():
    assert elevenlabs_dubbing_language_code("ceb") == "ceb"
    assert elevenlabs_dubbing_language_code("yue") == "yue"


def test_all_supported_languages_have_dubbing_codes():
    assert_supported_languages_mapped()
    for code in SUPPORTED_LANGUAGES:
        assert elevenlabs_dubbing_language_code(code)
