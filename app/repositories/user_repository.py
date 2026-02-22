"""
Repository for User CRUD operations.
Uses async SQLAlchemy 2.x query API.
"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create(
        self,
        email: str,
        username: str,
        hashed_password: str,
        full_name: Optional[str] = None,
    ) -> User:
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
        )
        self.db.add(user)
        await self.db.flush()  # populate id before commit
        await self.db.refresh(user)
        return user

    async def deactivate(self, user: User) -> User:
        user.is_active = False
        await self.db.flush()
        return user
