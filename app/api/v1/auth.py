"""
Auth API router — register, login, token refresh, and current user.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    LoginResponse,
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    body: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Create a new account with email, username, and password."""
    service = AuthService(db)
    user = await service.register(body)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Authenticate and receive JWT tokens",
)
async def login(
    body: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """Exchange credentials for access + refresh tokens."""
    service = AuthService(db)
    user, tokens = await service.login(body.email, body.password)
    return LoginResponse(
        user=UserResponse.model_validate(user),
        tokens=tokens,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
async def refresh_token(
    body: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Obtain a new access token using a valid refresh token."""
    service = AuthService(db)
    return await service.refresh(body.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user",
)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return the profile of the currently authenticated user."""
    return UserResponse.model_validate(current_user)
