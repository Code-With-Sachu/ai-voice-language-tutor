"""
Text-to-speech: converts the corrected sentence into playable audio bytes
using gTTS (Google Text-to-Speech), spoken in the learner's target language.
"""

import io
from gtts import gTTS, gTTSError


class TextToSpeechError(Exception):
    """Raised when text-to-speech synthesis fails."""
    pass


def synthesize_speech(text: str, gtts_lang_code: str) -> bytes:
    """
    Converts text into MP3 audio bytes using gTTS, spoken in the given language.

    Args:
        text: The text to speak.
        gtts_lang_code: gTTS language code (e.g. "es", "fr", "ja").

    Returns:
        Raw MP3 audio bytes.

    Raises:
        TextToSpeechError: If synthesis fails (e.g. no internet, empty text).
    """
    if not text.strip():
        raise TextToSpeechError("Cannot synthesize speech for empty text.")

    try:
        tts = gTTS(text=text, lang=gtts_lang_code)
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer.read()
    except gTTSError as e:
        raise TextToSpeechError(f"Text-to-speech synthesis failed: {e}") from e
    except Exception as e:  # noqa: BLE001 - gTTS can raise generic errors on network issues
        raise TextToSpeechError(f"Text-to-speech synthesis failed: {e}") from e
