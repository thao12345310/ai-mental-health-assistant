"""
Mood tracking API router.
"""
from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repositories.mood_repository import MoodRepository
from app.schemas.mood import MoodCreateRequest, MoodHistoryResponse, MoodResponse

router = APIRouter(prefix="/mood", tags=["Mood Tracking"])


@router.post(
    "/",
    response_model=MoodResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log a daily mood entry",
)
async def log_mood(
    body: MoodCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MoodResponse:
    """Record a mood score (1–10) with an optional note for today."""
    repo = MoodRepository(db)
    entry = await repo.create_entry(
        user_id=current_user.id,
        score=body.score,
        note=body.note,
    )
    return MoodResponse.model_validate(entry)


@router.get(
    "/history",
    response_model=MoodHistoryResponse,
    summary="Get mood history",
)
async def mood_history(
    limit: int = Query(default=30, ge=1, le=100, description="Number of entries to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MoodHistoryResponse:
    """Return the most recent `limit` mood entries and their average score."""
    repo = MoodRepository(db)
    entries = await repo.get_history(current_user.id, limit=limit)
    avg = await repo.get_average(current_user.id)
    return MoodHistoryResponse(
        entries=[MoodResponse.model_validate(e) for e in entries],
        average_score=avg,
        total_entries=len(entries),
    )
