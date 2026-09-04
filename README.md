# 🗣️ AI Voice Language Tutor

A learner speaks a sentence in a language they're learning; the app transcribes it, checks grammar and word choice with an LLM, and speaks back a corrected version.

## What it does

1. **Pick a target language** from a dropdown (Spanish, French, German, Italian, Portuguese, Japanese, Mandarin, English)
2. **Record or upload** a spoken sentence in that language
3. **Transcribes** it using the OpenAI Whisper API (with a language hint for better accuracy)
4. **Checks grammar and vocabulary** with GPT, which returns:
   - Whether the sentence was correct
   - A corrected, natural version
   - A plain-English explanation of the fix
   - Specific mistakes identified
   - A short line of encouragement
5. **Speaks the corrected sentence back** in the target language using gTTS

## Tech Stack

| Component        | Choice                          |
|-------------------|-----------------------------------|
| Speech-to-text    | OpenAI Whisper API (`whisper-1`)  |
| Feedback LLM      | OpenAI GPT (`gpt-4o-mini`)        |
| Text-to-speech    | gTTS (free, no API key required)  |
| UI                | Streamlit                         |

## Project Structure

```
ai-voice-language-tutor/
├── main.py                  # Streamlit app entry point (UI)
├── app/
│   ├── config.py              # Settings, API key loading, supported languages
│   ├── transcription.py       # Whisper API wrapper (with language hint)
│   ├── feedback.py            # GPT-based grammar/vocab feedback + correction
│   └── tts.py                 # gTTS wrapper (multi-language)
├── tests/
│   ├── test_config.py         # Language data integrity tests
│   ├── test_feedback.py       # Mocked GPT feedback tests
│   ├── test_transcription.py  # Mocked Whisper tests
│   └── test_tts.py            # Mocked TTS tests
├── sample_audio/              # Drop test audio clips here (gitignored)
├── .streamlit/config.toml
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd ai-voice-language-tutor
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Add your OpenAI API key

```bash
cp .env.example .env
```

Edit `.env`:

```
OPENAI_API_KEY=sk-your-actual-key-here
```

Get a key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys).

### 3. Run the app

```bash
streamlit run main.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`).

## Usage

1. Choose the language you're practicing from the dropdown.
2. **Record** a sentence with your microphone or **upload** an audio file.
3. Click **"✨ Check My Sentence"**.
4. Review:
   - What you said (transcribed)
   - The corrected, natural version — with an audio player so you can hear it spoken
   - An explanation of what was wrong (if anything)
   - Specific mistakes called out
   - A quick word of encouragement

## Adding a new language

Edit `app/config.py` and add an entry to `SUPPORTED_LANGUAGES`:

```python
SUPPORTED_LANGUAGES = {
    ...
    "Korean": {"gtts_code": "ko", "whisper_hint": "ko"},
}
```

- `gtts_code` must be a language code [supported by gTTS](https://gtts.readthedocs.io/en/latest/module.html#localized-accents).
- `whisper_hint` should be the ISO-639-1 code Whisper expects.

No other code changes are needed.

## Running tests

```bash
pip install pytest
pytest tests/ -v
```

All 17 tests mock external calls (OpenAI, gTTS), so they run offline without real API keys.

## Notes & Limitations

- Transcription accuracy depends on audio clarity, accent, and background noise — this can occasionally introduce artifacts that look like "mistakes" in the learner's speech. The feedback prompt is written to be forgiving of likely transcription errors, but it's not perfect.
- **gTTS requires internet access** to Google's Translate TTS endpoint at runtime.
- The OpenAI Whisper API has a hard 25 MB file size limit per request.
- This version does not track progress across sessions or adapt difficulty — each check is independent (see stretch goal below).
- The app is stateless between sessions — nothing is saved to disk.

## Possible Extensions (stretch goal, not implemented here)

- Track a learner's mistakes and progress across sessions (would need a database)
- Adapt sentence difficulty or suggest practice topics based on recurring mistake patterns
- Auto-detect the spoken language instead of requiring a fixed selection
- Add a "practice mode" that suggests sentences to translate/speak

## License

MIT — see [LICENSE](LICENSE).
