"""
Repository for mood entries, emotion logs, and crisis events.
"""
import json
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import CrisisEvent, EmotionLog, MoodEntry


class MoodRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_entry(
        self, user_id: int, score: int, note: Optional[str] = None
    ) -> MoodEntry:
        entry = MoodEntry(user_id=user_id, score=score, note=note)
        self.db.add(entry)
        await self.db.flush()
        await self.db.refresh(entry)
        return entry

    async def get_history(
        self, user_id: int, limit: int = 30
    ) -> List[MoodEntry]:
        result = await self.db.execute(
            select(MoodEntry)
            .where(MoodEntry.user_id == user_id)
            .order_by(MoodEntry.logged_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_average(self, user_id: int) -> Optional[float]:
        result = await self.db.execute(
            select(func.avg(MoodEntry.score)).where(MoodEntry.user_id == user_id)
        )
        avg = result.scalar_one_or_none()
        return round(float(avg), 2) if avg is not None else None


class EmotionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_log(
        self,
        message_id: int,
        primary_emotion: str,
        confidence: float,
        all_scores: Optional[dict] = None,
    ) -> EmotionLog:
        log = EmotionLog(
            message_id=message_id,
            primary_emotion=primary_emotion,
            confidence=confidence,
            all_scores=json.dumps(all_scores) if all_scores else None,
        )
        self.db.add(log)
        await self.db.flush()
        await self.db.refresh(log)
        return log


class CrisisRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_event(
        self,
        user_id: int,
        message_snippet: str,
        trigger_keywords: List[str],
    ) -> CrisisEvent:
        event = CrisisEvent(
            user_id=user_id,
            message_snippet=message_snippet[:500],
            trigger_keywords=json.dumps(trigger_keywords),
        )
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(event)
        return event

    async def get_user_events(self, user_id: int) -> List[CrisisEvent]:
        result = await self.db.execute(
            select(CrisisEvent)
            .where(CrisisEvent.user_id == user_id)
            .order_by(CrisisEvent.detected_at.desc())
        )
        return list(result.scalars().all())
