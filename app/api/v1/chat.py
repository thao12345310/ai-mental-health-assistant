"""
Chat API router — sessions, messaging, and history.
"""
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat import (
    ChatHistoryResponse,
    ChatSendRequest,
    ChatSendResponse,
    ChatSessionResponse,
    EmotionResult,
    MessageResponse,
)
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "/send",
    response_model=ChatSendResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message to the AI assistant",
)
async def send_message(
    body: ChatSendRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatSendResponse:
    """
    Send a user message. The service will:
    - Screen for crisis signals (highest priority)
    - Generate an empathetic AI response
    - Analyse the emotional tone
    - Persist everything to the database

    Provide `session_id` to continue an existing conversation,
    or omit it to start a new one.
    """
    service = ChatService(db)
    result = await service.send_message(
        user=current_user,
        content=body.message,
        session_id=body.session_id,
    )

    emotion = (
        EmotionResult(**result["emotion"]) if result.get("emotion") else None
    )

    return ChatSendResponse(
        session_id=result["session"].id,
        user_message=MessageResponse.model_validate(result["user_message"]),
        ai_response=MessageResponse.model_validate(result["ai_response"]),
        emotion=emotion,
        crisis_detected=result["crisis_detected"],
        crisis_message=result.get("crisis_message"),
    )


@router.get(
    "/sessions",
    response_model=List[ChatSessionResponse],
    summary="List all chat sessions for the current user",
)
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[ChatSessionResponse]:
    """Return all chat sessions for the authenticated user, newest first."""
    service = ChatService(db)
    sessions = await service.list_sessions(current_user)
    return [ChatSessionResponse.model_validate(s) for s in sessions]


@router.get(
    "/sessions/{session_id}",
    response_model=ChatHistoryResponse,
    summary="Get full message history of a session",
)
async def get_session_history(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatHistoryResponse:
    """Retrieve the complete message history for a specific session."""
    service = ChatService(db)
    session = await service.get_session_history(current_user, session_id)
    return ChatHistoryResponse(
        session=ChatSessionResponse.model_validate(session),
        messages=[MessageResponse.model_validate(m) for m in session.messages],
    )
