from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import hash_password
from models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, username: str, email: str, password: str) -> User:
        new_user = User(
            username=username, email=email, password_hash=hash_password(password)
        )

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        return new_user

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()

        return user

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(
            select(User).where(func.lower(User.username) == username.lower()),
        )
        user = result.scalars().first()

        return user

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(func.lower(User.email) == email),
        )
        user = result.scalars().first()

        return user

    async def update(self, user: User, update_data: dict[str, Any]) -> User:
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def update_profile_picture(self, user: User, new_filename: str) -> None:
        user.image_file = new_filename
        await self.db.commit()
        await self.db.refresh(user)

    async def delete(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.commit()

    async def delete_profile_picture(self, user: User) -> None:
        user.image_file = None
        await self.db.commit()
        await self.db.refresh(user)
