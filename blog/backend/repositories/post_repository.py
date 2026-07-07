from collections.abc import Sequence
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models as models


class PostRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, title: str, content: str, user_id: int) -> models.Post:
        new_post = models.Post(title=title, content=content, user_id=user_id)

        self.db.add(new_post)
        await self.db.commit()
        await self.db.refresh(new_post, attribute_names=["author"])

        return new_post

    async def delete(self, post: models.Post) -> None:
        await self.db.delete(post)
        await self.db.commit()

    async def get_by_id(self, post_id: int) -> models.Post | None:
        result = await self.db.execute(
            select(models.Post).where(models.Post.id == post_id),
        )
        return result.scalars().first()

    async def get_post_with_author(self, post_id: int) -> models.Post | None:
        result = await self.db.execute(
            select(models.Post)
            .options(selectinload(models.Post.author))
            .where(models.Post.id == post_id)
        )
        return result.scalars().first()

    async def get_paginated(self, skip: int, limit: int) -> Sequence[models.Post]:
        result = await self.db.execute(
            select(models.Post)
            .options(selectinload(models.Post.author))
            .order_by(models.Post.date_posted.desc())
            .offset(skip)
            .limit(limit),
        )
        return result.scalars().all()

    async def update(
        self, post: models.Post, update_data: dict[str, Any]
    ) -> models.Post:
        for field, value in update_data.items():
            setattr(post, field, value)

        await self.db.commit()
        await self.db.refresh(post, attribute_names=["author"])

        return post

    async def count(self) -> int:
        count_result = await self.db.execute(
            select(func.count()).select_from(models.Post)
        )
        total = count_result.scalar() or 0

        return total
