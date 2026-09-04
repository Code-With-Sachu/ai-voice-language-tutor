"""
Unit tests for app.config — verifies the supported languages data is
well-formed, since main.py and tts.py rely on its structure.
"""

from app.config import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE


def test_supported_languages_not_empty():
    assert len(SUPPORTED_LANGUAGES) > 0


def test_each_language_has_required_keys():
    for name, config in SUPPORTED_LANGUAGES.items():
        assert "gtts_code" in config, f"{name} missing gtts_code"
        assert "whisper_hint" in config, f"{name} missing whisper_hint"
        assert config["gtts_code"], f"{name} has empty gtts_code"
        assert config["whisper_hint"], f"{name} has empty whisper_hint"


def test_default_language_is_in_supported_languages():
    assert DEFAULT_LANGUAGE in SUPPORTED_LANGUAGES


def test_language_names_are_unique():
    names = list(SUPPORTED_LANGUAGES.keys())
    assert len(names) == len(set(names))
