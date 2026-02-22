"""
Repository for chat sessions and messages.
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import ChatSession, Message


class ChatRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Sessions ──────────────────────────────────────────────────────────────

    async def create_session(self, user_id: int, title: Optional[str] = None) -> ChatSession:
        session = ChatSession(user_id=user_id, title=title)
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def get_session(self, session_id: int, user_id: int) -> Optional[ChatSession]:
        result = await self.db.execute(
            select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_user_sessions(self, user_id: int) -> List[ChatSession]:
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
        )
        return list(result.scalars().all())

    async def get_session_with_messages(
        self, session_id: int, user_id: int
    ) -> Optional[ChatSession]:
        result = await self.db.execute(
            select(ChatSession)
            .options(selectinload(ChatSession.messages))
            .where(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    # ── Messages ──────────────────────────────────────────────────────────────

    async def create_message(
        self, session_id: int, role: str, content: str
    ) -> Message:
        message = Message(session_id=session_id, role=role, content=content)
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def get_recent_messages(
        self, session_id: int, limit: int = 20
    ) -> List[Message]:
        """Fetch recent messages for AI context window."""
        result = await self.db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = list(result.scalars().all())
        return list(reversed(messages))  # chronological order
