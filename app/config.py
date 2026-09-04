"""
Configuration and constants for the AI Voice Language Tutor.
"""

import os

# Load .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ---------------------------------------------------------------------------
# API configuration
# ---------------------------------------------------------------------------

# First, try environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# If running on Streamlit Cloud, try Streamlit Secrets
if not OPENAI_API_KEY:
    try:
        import streamlit as st
        OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        pass


# Models
TRANSCRIPTION_MODEL = "whisper-1"
FEEDBACK_MODEL = "gpt-4o-mini"


# ---------------------------------------------------------------------------
# App settings
# ---------------------------------------------------------------------------

APP_TITLE = "🗣️ AI Voice Language Tutor"

APP_DESCRIPTION = (
    "Speak a sentence in the language you're learning. The tutor transcribes it, "
    "checks your grammar and word choice, and reads back the corrected version."
)

MAX_FILE_SIZE_MB = 25

SUPPORTED_FORMATS = [
    "mp3",
    "mp4",
    "mpeg",
    "mpga",
    "m4a",
    "wav",
    "webm",
]


# Target languages the learner can practice.
SUPPORTED_LANGUAGES = {
    "Spanish": {"gtts_code": "es", "whisper_hint": "es"},
    "French": {"gtts_code": "fr", "whisper_hint": "fr"},
    "German": {"gtts_code": "de", "whisper_hint": "de"},
    "Italian": {"gtts_code": "it", "whisper_hint": "it"},
    "Portuguese": {"gtts_code": "pt", "whisper_hint": "pt"},
    "Japanese": {"gtts_code": "ja", "whisper_hint": "ja"},
    "Mandarin Chinese": {"gtts_code": "zh-CN", "whisper_hint": "zh"},
    "English": {"gtts_code": "en", "whisper_hint": "en"},
}

DEFAULT_LANGUAGE = "Spanish"


def keys_configured() -> bool:
    """Returns True if the OpenAI API key is configured."""
    return bool(OPENAI_API_KEY)