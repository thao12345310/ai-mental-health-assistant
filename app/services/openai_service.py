"""
Backward-compatible shim — delegates to the unified ai_provider module.
Kept so existing imports in chat_service.py continue to work unchanged.
"""
from app.services.ai_provider import get_ai_response  # noqa: F401

__all__ = ["get_ai_response"]
