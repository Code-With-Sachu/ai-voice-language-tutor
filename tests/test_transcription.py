"""
Unit tests for app.transcription. Uses mocking so no real API calls are made.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.transcription import transcribe_audio, TranscriptionError


@patch("app.transcription.OPENAI_API_KEY", "fake-key")
@patch("app.transcription.OpenAI")
def test_transcribe_audio_success(mock_openai_cls):
    mock_response = MagicMock()
    mock_response.text = "Soy feliz hoy."
    mock_client = MagicMock()
    mock_client.audio.transcriptions.create.return_value = mock_response
    mock_openai_cls.return_value = mock_client

    result = transcribe_audio(b"fake audio bytes", "sentence.wav", language_hint="es")

    assert result == "Soy feliz hoy."
    _, kwargs = mock_client.audio.transcriptions.create.call_args
    assert kwargs["language"] == "es"


@patch("app.transcription.OPENAI_API_KEY", "fake-key")
@patch("app.transcription.OpenAI")
def test_transcribe_audio_without_language_hint(mock_openai_cls):
    mock_response = MagicMock()
    mock_response.text = "Hello there."
    mock_client = MagicMock()
    mock_client.audio.transcriptions.create.return_value = mock_response
    mock_openai_cls.return_value = mock_client

    transcribe_audio(b"fake audio bytes", "sentence.wav")

    _, kwargs = mock_client.audio.transcriptions.create.call_args
    assert "language" not in kwargs


@patch("app.transcription.OPENAI_API_KEY", "")
def test_transcribe_audio_missing_api_key():
    with pytest.raises(TranscriptionError, match="API key is not configured"):
        transcribe_audio(b"fake audio bytes", "sentence.wav")


@patch("app.transcription.OPENAI_API_KEY", "fake-key")
@patch("app.transcription.OpenAI")
def test_transcribe_audio_empty_result_raises(mock_openai_cls):
    mock_response = MagicMock()
    mock_response.text = ""
    mock_client = MagicMock()
    mock_client.audio.transcriptions.create.return_value = mock_response
    mock_openai_cls.return_value = mock_client

    with pytest.raises(TranscriptionError, match="empty text"):
        transcribe_audio(b"fake audio bytes", "sentence.wav")
