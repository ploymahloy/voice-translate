"""ISO 639-3 (app API) to ISO 639-1 (ElevenLabs dubbing) mappings."""

from server.config import SUPPORTED_LANGUAGES

# ElevenLabs dubbing audio URLs use ISO 639-1 when a two-letter code exists.
_ISO639_3_TO_639_1: dict[str, str] = {
    "afr": "af",
    "ara": "ar",
    "asm": "as",
    "aze": "az",
    "bel": "be",
    "ben": "bn",
    "bos": "bs",
    "bul": "bg",
    "cat": "ca",
    "ces": "cs",
    "cym": "cy",
    "dan": "da",
    "deu": "de",
    "ell": "el",
    "eng": "en",
    "est": "et",
    "fin": "fi",
    "fra": "fr",
    "gle": "ga",
    "glg": "gl",
    "guj": "gu",
    "hau": "ha",
    "heb": "he",
    "hin": "hi",
    "hrv": "hr",
    "hye": "hy",
    "ind": "id",
    "isl": "is",
    "ita": "it",
    "jav": "jv",
    "kan": "kn",
    "kat": "ka",
    "kaz": "kk",
    "kir": "ky",
    "kor": "ko",
    "lav": "lv",
    "lin": "ln",
    "lit": "lt",
    "ltz": "lb",
    "mal": "ml",
    "mar": "mr",
    "msa": "ms",
    "nep": "ne",
    "nld": "nl",
    "nor": "no",
    "nya": "ny",
    "ori": "or",
    "pan": "pa",
    "pol": "pl",
    "por": "pt",
    "pus": "ps",
    "ron": "ro",
    "rus": "ru",
    "slk": "sk",
    "slv": "sl",
    "som": "so",
    "spa": "es",
    "srp": "sr",
    "swe": "sv",
    "swa": "sw",
    "tam": "ta",
    "tel": "te",
    "tgl": "tl",
    "tha": "th",
    "tur": "tr",
    "ukr": "uk",
    "urd": "ur",
    "vie": "vi",
    "yor": "yo",
    "zho": "zh",
    "zul": "zu",
}


def elevenlabs_dubbing_language_code(iso639_3: str) -> str:
    """Return the language code ElevenLabs dubbing expects for API calls."""
    return _ISO639_3_TO_639_1.get(iso639_3, iso639_3)


def assert_supported_languages_mapped() -> None:
    """Ensure every supported language resolves to a dubbing code."""
    for code in SUPPORTED_LANGUAGES:
        mapped = elevenlabs_dubbing_language_code(code)
        if not mapped:
            raise ValueError(f"Missing dubbing language mapping for {code!r}")
