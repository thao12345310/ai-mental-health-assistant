"""
OpenAI chat service — wraps the chat completion API with the mental health
system prompt and injects message history for contextual responses.
"""
import logging
from typing import List

from openai import AsyncOpenAI

from app.core.config import settings
from app.models.user import Message

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a mental health support assistant.
You are empathetic, calm, and supportive.
You do not diagnose medical conditions or prescribe medicine.
You listen actively, validate feelings, and offer coping strategies.
You prioritize user safety at all times.
If a user expresses a crisis, immediately encourage them to seek professional help
and provide crisis hotline information before anything else.
Keep responses concise (2-4 paragraphs) and human, never clinical or robotic."""

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


def _build_history(messages: List[Message]) -> List[dict]:
    """Convert ORM Message objects to OpenAI message dicts."""
    return [{"role": m.role, "content": m.content} for m in messages]


async def get_ai_response(
    user_message: str,
    history: List[Message],
) -> str:
    """
    Call the OpenAI Chat Completions API.

    Args:
        user_message: The latest message from the user.
        history: Previous messages in the session (for context window).

    Returns:
        The assistant's reply as a plain string.
    """
    messages = [{"role": "system", "content": _SYSTEM_PROMPT}]
    messages.extend(_build_history(history))
    messages.append({"role": "user", "content": user_message})

    try:
        client = _get_client()
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            max_tokens=settings.OPENAI_MAX_TOKENS,
            temperature=settings.OPENAI_TEMPERATURE,
        )
        content = response.choices[0].message.content
        return (content or "").strip()
    except Exception as exc:
        logger.error("OpenAI API error: %s", exc)
        raise RuntimeError(
            "The AI assistant is temporarily unavailable. Please try again shortly."
        ) from exc
