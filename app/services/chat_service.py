"""
Chat service — orchestrates sending a message, crisis detection,
AI response, emotion analysis, and persistence.
"""
import logging
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import ChatSession, Message, User
from app.repositories.chat_repository import ChatRepository
from app.repositories.mood_repository import CrisisRepository, EmotionRepository
from app.services.crisis_service import CRISIS_RESPONSE_MESSAGE, assess_crisis
from app.services.emotion_service import analyse_emotion
from app.services.openai_service import get_ai_response

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, db: AsyncSession) -> None:
        self.chat_repo = ChatRepository(db)
        self.emotion_repo = EmotionRepository(db)
        self.crisis_repo = CrisisRepository(db)

    # ── Session helpers ───────────────────────────────────────────────────────

    async def get_or_create_session(
        self, user: User, session_id: Optional[int]
    ) -> ChatSession:
        if session_id:
            session = await self.chat_repo.get_session(session_id, user.id)
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat session not found.",
                )
            return session
        return await self.chat_repo.create_session(user.id)

    async def list_sessions(self, user: User) -> List[ChatSession]:
        return await self.chat_repo.get_user_sessions(user.id)

    async def get_session_history(
        self, user: User, session_id: int
    ) -> ChatSession:
        session = await self.chat_repo.get_session_with_messages(session_id, user.id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found.",
            )
        return session

    # ── Core send ─────────────────────────────────────────────────────────────

    async def send_message(
        self,
        user: User,
        content: str,
        session_id: Optional[int] = None,
    ) -> dict:
        """
        Full pipeline:
          1. Resolve / create session
          2. Persist user message
          3. Crisis check → short-circuit if detected
          4. Fetch history → call OpenAI
          5. Persist AI reply
          6. Analyse emotion
          7. Return consolidated result dict
        """
        session = await self.get_or_create_session(user, session_id)

        # 1. Persist user message
        user_msg = await self.chat_repo.create_message(
            session_id=session.id, role="user", content=content
        )

        # 2. Crisis detection — highest priority
        assessment = assess_crisis(content)
        if assessment.is_crisis:
            logger.warning(
                "Crisis detected for user_id=%s severity=%s keywords=%s",
                user.id,
                assessment.severity,
                assessment.matched_keywords,
            )
            # Log crisis event (fire-and-forget within same transaction)
            await self.crisis_repo.create_event(
                user_id=user.id,
                message_snippet=content,
                trigger_keywords=assessment.matched_keywords,
            )
            # Store crisis response as assistant message too
            ai_msg = await self.chat_repo.create_message(
                session_id=session.id,
                role="assistant",
                content=CRISIS_RESPONSE_MESSAGE,
            )
            return {
                "session": session,
                "user_message": user_msg,
                "ai_response": ai_msg,
                "emotion": None,
                "crisis_detected": True,
                "crisis_message": CRISIS_RESPONSE_MESSAGE,
            }

        # 3. Fetch recent history for context window
        history = await self.chat_repo.get_recent_messages(session.id, limit=20)
        # Exclude the message we just inserted (it's the last one)
        history = [m for m in history if m.id != user_msg.id]

        # 4. AI response
        try:
            ai_text = await get_ai_response(content, history)
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            )

        ai_msg = await self.chat_repo.create_message(
            session_id=session.id, role="assistant", content=ai_text
        )

        # 5. Emotion analysis (non-blocking; failure doesn't break the response)
        emotion_data = None
        try:
            primary_emotion, confidence = await analyse_emotion(content)
            await self.emotion_repo.create_log(
                message_id=user_msg.id,
                primary_emotion=primary_emotion,
                confidence=confidence,
            )
            emotion_data = {"primary_emotion": primary_emotion, "confidence": confidence}
        except Exception as exc:
            logger.warning("Emotion logging failed: %s", exc)

        return {
            "session": session,
            "user_message": user_msg,
            "ai_response": ai_msg,
            "emotion": emotion_data,
            "crisis_detected": False,
            "crisis_message": None,
        }
