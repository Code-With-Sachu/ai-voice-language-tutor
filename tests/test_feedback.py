"""
Unit tests for app.feedback. Uses mocking so no real API calls are made.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from app.feedback import get_feedback, FeedbackError, TutorFeedback


def _mock_openai_response(payload: dict):
    mock_message = MagicMock()
    mock_message.content = json.dumps(payload)
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    return mock_response


@patch("app.feedback.OPENAI_API_KEY", "fake-key")
@patch("app.feedback.OpenAI")
def test_get_feedback_incorrect_sentence(mock_openai_cls):
    payload = {
        "is_correct": False,
        "corrected_sentence": "Estoy feliz hoy.",
        "explanation": "'Soy' is used for permanent traits, 'estoy' for temporary states like feelings.",
        "mistakes": ["wrong verb: 'soy' should be 'estoy' for temporary states"],
        "encouragement": "Great effort — this is a very common mix-up!",
    }
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _mock_openai_response(payload)
    mock_openai_cls.return_value = mock_client

    result = get_feedback("Soy feliz hoy.", "Spanish")

    assert isinstance(result, TutorFeedback)
    assert result.is_correct is False
    assert result.corrected_sentence == "Estoy feliz hoy."
    assert len(result.mistakes) == 1
    assert result.original_sentence == "Soy feliz hoy."
    assert result.encouragement


@patch("app.feedback.OPENAI_API_KEY", "fake-key")
@patch("app.feedback.OpenAI")
def test_get_feedback_correct_sentence(mock_openai_cls):
    payload = {
        "is_correct": True,
        "corrected_sentence": "Estoy feliz hoy.",
        "explanation": "This sentence is grammatically correct and natural.",
        "mistakes": [],
        "encouragement": "Perfect!",
    }
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _mock_openai_response(payload)
    mock_openai_cls.return_value = mock_client

    result = get_feedback("Estoy feliz hoy.", "Spanish")

    assert result.is_correct is True
    assert result.mistakes == []


@patch("app.feedback.OPENAI_API_KEY", "fake-key")
@patch("app.feedback.OpenAI")
def test_get_feedback_passes_language_into_system_prompt(mock_openai_cls):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _mock_openai_response(
        {"is_correct": True, "corrected_sentence": "Bonjour.", "explanation": "", "mistakes": [], "encouragement": ""}
    )
    mock_openai_cls.return_value = mock_client

    get_feedback("Bonjour.", "French")

    _, kwargs = mock_client.chat.completions.create.call_args
    system_message = kwargs["messages"][0]["content"]
    assert "French" in system_message


@patch("app.feedback.OPENAI_API_KEY", "")
def test_get_feedback_missing_api_key():
    with pytest.raises(FeedbackError, match="API key is not configured"):
        get_feedback("Hola.", "Spanish")


@patch("app.feedback.OPENAI_API_KEY", "fake-key")
def test_get_feedback_empty_sentence():
    with pytest.raises(FeedbackError, match="empty sentence"):
        get_feedback("   ", "Spanish")


@patch("app.feedback.OPENAI_API_KEY", "fake-key")
@patch("app.feedback.OpenAI")
def test_get_feedback_invalid_json(mock_openai_cls):
    mock_message = MagicMock()
    mock_message.content = "not valid json {{"
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_cls.return_value = mock_client

    with pytest.raises(FeedbackError, match="Could not parse"):
        get_feedback("Hola.", "Spanish")
