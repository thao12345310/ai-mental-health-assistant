"""
Authentication service — orchestrates user registration, login, and token refresh.
"""
import logging
from typing import Tuple

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse, UserRegisterRequest

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)

    async def register(self, data: UserRegisterRequest) -> User:
        """Create a new user account. Raises 409 on duplicates."""
        if await self.repo.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )
        if await self.repo.get_by_username(data.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This username is already taken.",
            )

        hashed = hash_password(data.password)
        user = await self.repo.create(
            email=data.email,
            username=data.username,
            hashed_password=hashed,
            full_name=data.full_name,
        )
        logger.info("New user registered: id=%s email=%s", user.id, user.email)
        return user

    async def login(self, email: str, password: str) -> Tuple[User, TokenResponse]:
        """Verify credentials and return tokens. Raises 401 on failure."""
        user = await self.repo.get_by_email(email)

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled. Please contact support.",
            )

        tokens = self._issue_tokens(user)
        return user, tokens

    async def refresh(self, refresh_token: str) -> TokenResponse:
        """Issue a new access token using a valid refresh token."""
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise ValueError("Not a refresh token")
            user_id = int(payload["sub"])
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token.",
            )

        user = await self.repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive.",
            )

        return self._issue_tokens(user)

    @staticmethod
    def _issue_tokens(user: User) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(user.id, user.email),
            refresh_token=create_refresh_token(user.id),
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
