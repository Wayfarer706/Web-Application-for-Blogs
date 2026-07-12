from collections.abc import Sequence
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.post import Post
from models.tag import Tag


class PostRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        title: str,
        content: str,
        user_id: int,
        category_id: int,
        tags: list[Tag],
    ) -> Post:
        new_post = Post(
            title=title,
            content=content,
            user_id=user_id,
            category_id=category_id,
            tags=tags,
        )

        self.db.add(new_post)
        await self.db.commit()
        await self.db.refresh(
            new_post, attribute_names=["author", "comments", "tags", "category"]
        )

        return new_post

    async def delete(self, post: Post) -> None:
        await self.db.delete(post)
        await self.db.commit()

    async def get_by_id(self, post_id: int) -> Post | None:
        result = await self.db.execute(
            select(Post).where(Post.id == post_id),
        )
        post = result.scalars().first()

        return post

    async def get_post_with_author(self, post_id: int) -> Post | None:
        result = await self.db.execute(
            select(Post).options(selectinload(Post.author)).where(Post.id == post_id)
        )
        post = result.scalars().first()

        return post

    async def get_paginated(self, skip: int, limit: int) -> Sequence[Post]:
        result = await self.db.execute(
            select(Post)
            .options(selectinload(Post.author))
            .order_by(Post.date_posted.desc())
            .offset(skip)
            .limit(limit),
        )
        posts = result.scalars().all()

        return posts

    async def update(self, post: Post, update_data: dict[str, Any]) -> Post:
        for field, value in update_data.items():
            setattr(post, field, value)

        await self.db.commit()
        await self.db.refresh(post, attribute_names=["author"])

        return post

    async def count(self) -> int:
        count_result = await self.db.execute(select(func.count()).select_from(Post))
        total = count_result.scalar() or 0

        return total

    async def count_user_posts(self, user_id: int) -> int:
        count_result = await self.db.execute(
            select(func.count()).select_from(Post).where(Post.user_id == user_id)
        )
        total = count_result.scalar() or 0

        return total

    async def get_user_posts_paginated(
        self, user_id: int, skip: int, limit: int
    ) -> Sequence[Post]:
        result = await self.db.execute(
            select(Post)
            .options(selectinload(Post.author))
            .where(Post.user_id == user_id)
            .order_by(Post.date_posted.desc())
            .offset(skip)
            .limit(limit),
        )
        posts = result.scalars().all()

        return posts
