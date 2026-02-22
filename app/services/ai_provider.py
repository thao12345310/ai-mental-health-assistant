"""
AI provider abstraction layer.

Supports three backends — select via AI_PROVIDER in .env:
  - "openrouter" → OpenRouter (200+ models, free tier, recommended)
  - "openai"     → OpenAI GPT models (requires OPENAI_API_KEY)
  - "gemini"     → Google Gemini native SDK (requires GEMINI_API_KEY)

OpenRouter uses the same OpenAI SDK — just a different base_url + api_key.
All providers share identical function signatures.
"""
import json
import logging
from typing import List, Tuple

from app.core.config import settings
from app.models.user import Message

logger = logging.getLogger(__name__)

# ── Shared system prompt ──────────────────────────────────────────────────────
_SYSTEM_PROMPT = """You are a mental health support assistant.
You are empathetic, calm, and supportive.
You do not diagnose medical conditions or prescribe medicine.
You listen actively, validate feelings, and offer coping strategies.
You prioritize user safety at all times.
If a user expresses a crisis, immediately encourage them to seek professional help
and provide crisis hotline information before anything else.
Keep responses concise (2-4 paragraphs) and human, never clinical or robotic."""

_EMOTIONS = [
    "happy", "sad", "anxious", "angry", "fearful",
    "disgusted", "surprised", "neutral", "hopeful", "overwhelmed",
]

_EMOTION_PROMPT = f"""You are an emotion classifier. Analyse the user message and return a JSON object
with exactly two keys:
  "emotion": one of {_EMOTIONS}
  "confidence": a float between 0.0 and 1.0

Respond ONLY with valid JSON. No explanation, no markdown fences."""


# ── OpenAI-compatible client helper ──────────────────────────────────────────
def _get_openai_client():
    """Standard OpenAI client."""
    from openai import AsyncOpenAI
    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


def _get_openrouter_client():
    """
    OpenRouter uses identical API to OpenAI — just override base_url.
    Pass extra headers so OpenRouter can track usage correctly.
    """
    from openai import AsyncOpenAI
    return AsyncOpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": settings.OPENROUTER_SITE_URL,
            "X-Title": settings.OPENROUTER_APP_NAME,
        },
    )


# ── OpenAI provider ───────────────────────────────────────────────────────────
async def _openai_chat(user_message: str, history: List[Message]) -> str:
    client = _get_openai_client()
    messages = [{"role": "system", "content": _SYSTEM_PROMPT}]
    messages.extend([{"role": m.role, "content": m.content} for m in history])
    messages.append({"role": "user", "content": user_message})

    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        max_tokens=settings.OPENAI_MAX_TOKENS,
        temperature=settings.OPENAI_TEMPERATURE,
    )
    return (response.choices[0].message.content or "").strip()


async def _openai_emotion(text: str) -> Tuple[str, float]:
    client = _get_openai_client()
    resp = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": _EMOTION_PROMPT},
            {"role": "user", "content": text[:1000]},
        ],
        max_tokens=60,
        temperature=0.0,
        response_format={"type": "json_object"},
    )
    return _parse_emotion_json(resp.choices[0].message.content or "{}")


# ── OpenRouter provider ───────────────────────────────────────────────────────
async def _openrouter_chat(user_message: str, history: List[Message]) -> str:
    client = _get_openrouter_client()
    messages = [{"role": "system", "content": _SYSTEM_PROMPT}]
    messages.extend([{"role": m.role, "content": m.content} for m in history])
    messages.append({"role": "user", "content": user_message})

    response = await client.chat.completions.create(
        model=settings.OPENROUTER_MODEL,
        messages=messages,
        max_tokens=settings.OPENAI_MAX_TOKENS,
        temperature=settings.OPENAI_TEMPERATURE,
    )
    return (response.choices[0].message.content or "").strip()


async def _openrouter_emotion(text: str) -> Tuple[str, float]:
    client = _get_openrouter_client()
    resp = await client.chat.completions.create(
        model=settings.OPENROUTER_MODEL,
        messages=[
            {"role": "system", "content": _EMOTION_PROMPT},
            {"role": "user", "content": text[:1000]},
        ],
        max_tokens=80,
        temperature=0.0,
    )
    raw = resp.choices[0].message.content or "{}"
    # Some models wrap JSON in markdown fences — strip them
    return _parse_emotion_json(_strip_md_fences(raw))


# ── Gemini provider (native SDK) ──────────────────────────────────────────────
async def _gemini_chat(user_message: str, history: List[Message]) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    contents = []
    for m in history:
        role = "user" if m.role == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m.content}]})
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    response = await client.aio.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=_SYSTEM_PROMPT,
            max_output_tokens=settings.OPENAI_MAX_TOKENS,
            temperature=settings.OPENAI_TEMPERATURE,
        ),
    )
    return response.text.strip()


async def _gemini_emotion(text: str) -> Tuple[str, float]:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    prompt = f"{_EMOTION_PROMPT}\n\nMessage to classify:\n{text[:1000]}"

    response = await client.aio.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.0, max_output_tokens=80),
    )
    return _parse_emotion_json(_strip_md_fences(response.text.strip()))


# ── JSON helpers ──────────────────────────────────────────────────────────────
def _strip_md_fences(text: str) -> str:
    """Remove ```json ... ``` fences that some models add."""
    t = text.strip()
    if t.startswith("```"):
        parts = t.split("```")
        # parts[1] is the content between first pair of fences
        t = parts[1]
        if t.startswith("json"):
            t = t[4:]
    return t.strip()


def _parse_emotion_json(raw: str) -> Tuple[str, float]:
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return "neutral", 0.5
    emotion = data.get("emotion", "neutral")
    confidence = float(data.get("confidence", 0.5))
    if emotion not in _EMOTIONS:
        emotion = "neutral"
    return emotion, max(0.0, min(1.0, confidence))


# ── Public API — router ───────────────────────────────────────────────────────
async def get_ai_response(user_message: str, history: List[Message]) -> str:
    """
    Route to the configured AI provider.
    Raises RuntimeError on failure (caught by ChatService → 503 response).
    """
    provider = settings.AI_PROVIDER.lower()
    logger.info("Using AI provider: %s", provider)
    try:
        if provider == "openrouter":
            return await _openrouter_chat(user_message, history)
        elif provider == "gemini":
            return await _gemini_chat(user_message, history)
        else:
            return await _openai_chat(user_message, history)
    except Exception as exc:
        logger.error("AI provider '%s' error: %s", provider, exc)
        raise RuntimeError(
            "The AI assistant is temporarily unavailable. Please try again shortly."
        ) from exc


async def analyse_emotion(text: str) -> Tuple[str, float]:
    """
    Route emotion analysis to the configured AI provider.
    Falls back to ('neutral', 0.5) on any error.
    """
    provider = settings.AI_PROVIDER.lower()
    try:
        if provider == "openrouter":
            return await _openrouter_emotion(text)
        elif provider == "gemini":
            return await _gemini_emotion(text)
        else:
            return await _openai_emotion(text)
    except Exception as exc:
        logger.warning("Emotion analysis failed (%s): %s", provider, exc)
        return "neutral", 0.5
