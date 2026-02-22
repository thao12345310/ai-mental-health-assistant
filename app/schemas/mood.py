"""
Pydantic schemas for mood tracking and emotion analysis endpoints.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


# ── Mood Tracking ─────────────────────────────────────────────────────────────

class MoodCreateRequest(BaseModel):
    score: int = Field(..., ge=1, le=10, description="Mood score from 1 (worst) to 10 (best)")
    note: Optional[str] = Field(None, max_length=1000)

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: int) -> int:
        if not 1 <= v <= 10:
            raise ValueError("Score must be between 1 and 10.")
        return v


class MoodResponse(BaseModel):
    id: int
    user_id: int
    score: int
    note: Optional[str]
    logged_at: datetime

    model_config = {"from_attributes": True}


class MoodHistoryResponse(BaseModel):
    entries: List[MoodResponse]
    average_score: Optional[float]
    total_entries: int


# ── Emotion Log ───────────────────────────────────────────────────────────────

class EmotionLogResponse(BaseModel):
    id: int
    message_id: int
    primary_emotion: str
    confidence: float
    analyzed_at: datetime

    model_config = {"from_attributes": True}


# ── Crisis Event ──────────────────────────────────────────────────────────────

class CrisisEventResponse(BaseModel):
    id: int
    user_id: int
    message_snippet: str
    trigger_keywords: str
    detected_at: datetime
    resolved: bool

    model_config = {"from_attributes": True}
