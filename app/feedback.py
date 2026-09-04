"""
Language tutoring feedback: given a learner's spoken sentence (transcribed)
and their target language, uses an LLM to check grammar/vocabulary and
produce a corrected version plus an explanation.
"""

import json
from dataclasses import dataclass, field

from openai import OpenAI, OpenAIError

from app.config import OPENAI_API_KEY, FEEDBACK_MODEL


class FeedbackError(Exception):
    """Raised when feedback generation fails."""
    pass


@dataclass
class TutorFeedback:
    """Structured result of analyzing a learner's spoken sentence."""
    is_correct: bool = False
    corrected_sentence: str = ""
    explanation: str = ""
    mistakes: list[str] = field(default_factory=list)
    encouragement: str = ""
    original_sentence: str = ""


SYSTEM_PROMPT = """You are a friendly, encouraging language tutor helping a learner practice \
speaking {language}. The learner just spoke a sentence in {language}, which was transcribed \
by speech-to-text (transcription errors are possible, so don't over-penalize odd words that \
might be transcription artifacts rather than real mistakes).

Analyze the sentence for grammar, word choice, and natural phrasing. Then:

1. Determine if the sentence is correct and natural as spoken (is_correct: true/false)
2. Provide a corrected, natural version of the sentence in {language} (if it was already \
correct, just repeat it as the corrected_sentence)
3. Write a short, clear explanation of what was wrong and why the correction is better \
(in English, 1-3 sentences). If the sentence was already correct, explain briefly why it's \
good or note any small style improvement.
4. List specific mistakes found (short phrases, e.g. "wrong verb conjugation: 'soy' should \
be 'estoy' for temporary states"). Empty list if no mistakes.
5. Write one short, warm sentence of encouragement for the learner.

Respond ONLY with valid JSON in this exact shape, no markdown fences, no extra text:
{{
  "is_correct": true,
  "corrected_sentence": "...",
  "explanation": "...",
  "mistakes": ["...", "..."],
  "encouragement": "..."
}}"""


def get_feedback(sentence: str, language: str) -> TutorFeedback:
    """
    Sends a transcribed learner sentence to the LLM and returns structured
    tutoring feedback.

    Args:
        sentence: The transcribed spoken sentence from the learner.
        language: The target language name (e.g. "Spanish").

    Returns:
        A TutorFeedback object.

    Raises:
        FeedbackError: If the API key is missing or the API call/parsing fails.
    """
    if not OPENAI_API_KEY:
        raise FeedbackError(
            "OpenAI API key is not configured. Set OPENAI_API_KEY in your environment "
            "or .env file."
        )

    if not sentence.strip():
        raise FeedbackError("Cannot generate feedback for an empty sentence.")

    client = OpenAI(api_key=OPENAI_API_KEY)
    system_prompt = SYSTEM_PROMPT.format(language=language)

    try:
        response = client.chat.completions.create(
            model=FEEDBACK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f'Learner said: "{sentence}"'},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
    except OpenAIError as e:
        raise FeedbackError(f"Feedback generation failed: {e}") from e

    content = response.choices[0].message.content

    try:
        data = json.loads(content)
    except (json.JSONDecodeError, TypeError) as e:
        raise FeedbackError(f"Could not parse model response as JSON: {e}") from e

    return TutorFeedback(
        is_correct=bool(data.get("is_correct", False)),
        corrected_sentence=str(data.get("corrected_sentence", "")).strip(),
        explanation=str(data.get("explanation", "")).strip(),
        mistakes=[str(m).strip() for m in data.get("mistakes", []) if str(m).strip()],
        encouragement=str(data.get("encouragement", "")).strip(),
        original_sentence=sentence,
    )
