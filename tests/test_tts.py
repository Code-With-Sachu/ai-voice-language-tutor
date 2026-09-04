"""
Unit tests for app.tts. Mocks gTTS so no network calls are made.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.tts import synthesize_speech, TextToSpeechError


@patch("app.tts.gTTS")
def test_synthesize_speech_success(mock_gtts_cls):
    mock_tts_instance = MagicMock()

    def fake_write_to_fp(buffer):
        buffer.write(b"fake-mp3-bytes")

    mock_tts_instance.write_to_fp.side_effect = fake_write_to_fp
    mock_gtts_cls.return_value = mock_tts_instance

    audio_bytes = synthesize_speech("Estoy feliz hoy.", "es")

    assert audio_bytes == b"fake-mp3-bytes"
    mock_gtts_cls.assert_called_once_with(text="Estoy feliz hoy.", lang="es")


def test_synthesize_speech_empty_text_raises():
    with pytest.raises(TextToSpeechError, match="empty text"):
        synthesize_speech("   ", "es")


@patch("app.tts.gTTS")
def test_synthesize_speech_wraps_generic_exceptions(mock_gtts_cls):
    mock_gtts_cls.side_effect = RuntimeError("network unreachable")

    with pytest.raises(TextToSpeechError, match="synthesis failed"):
        synthesize_speech("Bonjour.", "fr")
