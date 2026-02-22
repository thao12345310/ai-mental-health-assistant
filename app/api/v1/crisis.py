"""
Crisis events router — allows users (or admins) to list their crisis history.
"""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repositories.mood_repository import CrisisRepository
from app.schemas.mood import CrisisEventResponse

router = APIRouter(prefix="/crisis", tags=["Crisis Events"])


@router.get(
    "/events",
    response_model=List[CrisisEventResponse],
    summary="List crisis events for the current user",
)
async def list_crisis_events(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[CrisisEventResponse]:
    """
    Return all recorded crisis detections for the authenticated user.
    Useful for clinical follow-up or self-review.
    """
    repo = CrisisRepository(db)
    events = await repo.get_user_events(current_user.id)
    return [CrisisEventResponse.model_validate(e) for e in events]
