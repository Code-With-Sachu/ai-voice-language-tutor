"""
AI Voice Language Tutor
A learner speaks a sentence in a target language; the app transcribes it,
checks grammar and word choice with an LLM, and speaks back a corrected version.

Run with:  streamlit run main.py
"""

import streamlit as st

from app.config import (
    APP_TITLE,
    APP_DESCRIPTION,
    MAX_FILE_SIZE_MB,
    SUPPORTED_FORMATS,
    SUPPORTED_LANGUAGES,
    DEFAULT_LANGUAGE,
    keys_configured,
)
from app.transcription import transcribe_audio, TranscriptionError
from app.feedback import get_feedback, FeedbackError, TutorFeedback
from app.tts import synthesize_speech, TextToSpeechError

st.set_page_config(page_title="AI Voice Language Tutor", page_icon="🗣️", layout="centered")

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "tutor_result" not in st.session_state:
    st.session_state.tutor_result = None  # dict: {feedback, audio_bytes}
if "target_language" not in st.session_state:
    st.session_state.target_language = DEFAULT_LANGUAGE


def process_sentence(file_bytes: bytes, filename: str, language: str) -> dict:
    lang_config = SUPPORTED_LANGUAGES[language]

    with st.spinner(f"Transcribing your {language} sentence..."):
        transcript = transcribe_audio(file_bytes, filename, language_hint=lang_config["whisper_hint"])

    with st.spinner("Checking grammar and word choice..."):
        feedback = get_feedback(transcript, language)

    with st.spinner("Generating spoken correction..."):
        audio_bytes = synthesize_speech(feedback.corrected_sentence, lang_config["gtts_code"])

    return {"feedback": feedback, "audio_bytes": audio_bytes}


def render_feedback(feedback: TutorFeedback, audio_bytes: bytes):
    if feedback.is_correct:
        st.success("✅ Great job — your sentence was correct!")
    else:
        st.warning("📝 A few things to improve:")

    st.markdown("**You said:**")
    st.write(f"_{feedback.original_sentence}_")

    st.markdown("**Corrected version:**")
    st.write(f"**{feedback.corrected_sentence}**")
    st.audio(audio_bytes, format="audio/mp3")

    st.markdown("**Explanation:**")
    st.write(feedback.explanation or "_No explanation provided._")

    if feedback.mistakes:
        st.markdown("**Specific points:**")
        for m in feedback.mistakes:
            st.markdown(f"- {m}")

    if feedback.encouragement:
        st.info(feedback.encouragement, icon="💪")


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
st.title(APP_TITLE)
st.write(APP_DESCRIPTION)

if not keys_configured():
    st.error(
        "⚠️ OpenAI API key not found. Set the `OPENAI_API_KEY` environment variable "
        "(or add it to a `.env` file) before using this app."
    )
    st.stop()

st.divider()

st.session_state.target_language = st.selectbox(
    "🌍 Which language are you practicing?",
    options=list(SUPPORTED_LANGUAGES.keys()),
    index=list(SUPPORTED_LANGUAGES.keys()).index(st.session_state.target_language),
)

st.caption(f"Speak a sentence in **{st.session_state.target_language}** below.")

tab_record, tab_upload = st.tabs(["🎤 Record your sentence", "📁 Upload audio"])

sentence_bytes = None
sentence_filename = None

with tab_record:
    recorded_audio = st.audio_input("Say a sentence")
    if recorded_audio is not None:
        sentence_bytes = recorded_audio.read()
        sentence_filename = "sentence.wav"
        st.audio(sentence_bytes)

with tab_upload:
    uploaded_file = st.file_uploader(
        "Upload a spoken sentence",
        type=SUPPORTED_FORMATS,
        help=f"Max file size: {MAX_FILE_SIZE_MB} MB. Supported formats: {', '.join(SUPPORTED_FORMATS)}",
    )
    if uploaded_file is not None:
        size_mb = uploaded_file.size / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            st.error(f"File is {size_mb:.1f} MB, which exceeds the {MAX_FILE_SIZE_MB} MB limit.")
        else:
            sentence_bytes = uploaded_file.read()
            sentence_filename = uploaded_file.name
            st.audio(sentence_bytes)

st.divider()

check_clicked = st.button(
    "✨ Check My Sentence",
    type="primary",
    disabled=sentence_bytes is None,
    use_container_width=True,
)

if check_clicked and sentence_bytes is not None:
    try:
        result = process_sentence(sentence_bytes, sentence_filename, st.session_state.target_language)
        st.session_state.tutor_result = result
    except TranscriptionError as e:
        st.error(f"Transcription error: {e}")
    except FeedbackError as e:
        st.error(f"Feedback error: {e}")
    except TextToSpeechError as e:
        st.error(f"Text-to-speech error: {e}")
    except Exception as e:  # noqa: BLE001 - surface unexpected errors to the user
        st.error(f"Unexpected error: {e}")

if st.session_state.tutor_result is not None:
    st.divider()
    st.markdown("### 📋 Feedback")
    render_feedback(st.session_state.tutor_result["feedback"], st.session_state.tutor_result["audio_bytes"])

    if st.button("🗑️ Clear and try another sentence"):
        st.session_state.tutor_result = None
        st.rerun()

st.divider()
st.caption(
    "Built with Streamlit, OpenAI Whisper API (transcription), "
    "OpenAI GPT (grammar feedback), and gTTS (text-to-speech)."
)
