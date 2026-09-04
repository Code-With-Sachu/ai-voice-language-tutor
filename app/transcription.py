"""
Speech-to-text transcription using the OpenAI Whisper API, with an optional
language hint to improve accuracy when we already know the target language
the learner is practicing.
"""

import io
from openai import OpenAI, OpenAIError

from app.config import OPENAI_API_KEY, TRANSCRIPTION_MODEL


class TranscriptionError(Exception):
    """Raised when audio transcription fails."""
    pass


def transcribe_audio(file_bytes: bytes, filename: str, language_hint: str | None = None) -> str:
    """
    Sends audio bytes to the OpenAI Whisper API and returns the transcript text.

    Args:
        file_bytes: Raw bytes of the audio file.
        filename: Original filename (used so the API can infer the format).
        language_hint: Optional ISO-639-1 language code (e.g. "es", "fr") to
            improve transcription accuracy. Whisper will still auto-detect if
            the actual audio doesn't match, but the hint helps with accents
            and ambiguous words.

    Returns:
        The transcribed text.

    Raises:
        TranscriptionError: If the API key is missing or the API call fails.
    """
    if not OPENAI_API_KEY:
        raise TranscriptionError(
            "OpenAI API key is not configured. Set OPENAI_API_KEY in your environment "
            "or .env file."
        )

    client = OpenAI(api_key=OPENAI_API_KEY)

    audio_file = io.BytesIO(file_bytes)
    audio_file.name = filename

    kwargs = {"model": TRANSCRIPTION_MODEL, "file": audio_file}
    if language_hint:
        kwargs["language"] = language_hint

    try:
        response = client.audio.transcriptions.create(**kwargs)
    except OpenAIError as e:
        raise TranscriptionError(f"Transcription failed: {e}") from e

    transcript = getattr(response, "text", "").strip()
    if not transcript:
        raise TranscriptionError("Transcription returned empty text. Try a clearer recording.")

    return transcript
