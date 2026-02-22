"""
Backward-compatible shim — delegates to the unified ai_provider module.
Kept so existing imports in chat_service.py continue to work unchanged.
"""
from app.services.ai_provider import analyse_emotion  # noqa: F401

__all__ = ["analyse_emotion"]
