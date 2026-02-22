"""
Pydantic schemas for the chat system.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ── Chat Session ──────────────────────────────────────────────────────────────

class ChatSessionCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)


class ChatSessionResponse(BaseModel):
    id: int
    user_id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Message ───────────────────────────────────────────────────────────────────

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)


class MessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Chat Send / Reply ─────────────────────────────────────────────────────────

class ChatSendRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[int] = Field(
        None, description="Existing session ID; omit to create a new session."
    )


class EmotionResult(BaseModel):
    primary_emotion: str
    confidence: float


class ChatSendResponse(BaseModel):
    session_id: int
    user_message: MessageResponse
    ai_response: MessageResponse
    emotion: Optional[EmotionResult] = None
    crisis_detected: bool = False
    crisis_message: Optional[str] = None


# ── History ───────────────────────────────────────────────────────────────────

class ChatHistoryResponse(BaseModel):
    session: ChatSessionResponse
    messages: List[MessageResponse]
