"""
Emotion analysis service.

Uses GPT to classify the emotional tone of a user message into one of
a fixed set of emotions, returning a label + confidence score.
Falls back gracefully on API errors.
"""
import json
import logging
from typing import Optional, Tuple

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

_client: Optional[AsyncOpenAI] = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


_EMOTIONS = [
    "happy", "sad", "anxious", "angry", "fearful",
    "disgusted", "surprised", "neutral", "hopeful", "overwhelmed",
]

_EMOTION_PROMPT = f"""
You are an emotion classifier. Analyse the user message and return a JSON object
with exactly two keys:
  "emotion": one of {_EMOTIONS}
  "confidence": a float between 0.0 and 1.0

Respond ONLY with valid JSON. No explanation, no markdown fences.
""".strip()


async def analyse_emotion(text: str) -> Tuple[str, float]:
    """
    Classify the emotional tone of `text`.

    Returns (primary_emotion, confidence).
    Falls back to ("neutral", 0.5) on any error.
    """
    try:
        client = _get_client()
        resp = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": _EMOTION_PROMPT},
                {"role": "user", "content": text[:1000]},  # cap input length
            ],
            max_tokens=60,
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content or "{}"
        data = json.loads(raw)
        emotion = data.get("emotion", "neutral")
        confidence = float(data.get("confidence", 0.5))

        if emotion not in _EMOTIONS:
            emotion = "neutral"
        confidence = max(0.0, min(1.0, confidence))

        return emotion, confidence
    except Exception as exc:
        logger.warning("Emotion analysis failed: %s", exc)
        return "neutral", 0.5
