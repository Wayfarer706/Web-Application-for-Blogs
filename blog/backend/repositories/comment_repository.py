from collections.abc import Sequence
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.comment import Comment


class CommentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self, user_id: int, post_id: int, content: str, parent_id: int | None
    ) -> Comment:
        new_comment = Comment(
            user_id=user_id, post_id=post_id, content=content, parent_id=parent_id
        )

        self.db.add(new_comment)
        await self.db.commit()
        await self.db.refresh(new_comment, attribute_names=["author", "replies"])

        return new_comment

    async def get_by_id(self, comment_id: int) -> Comment | None:
        result = await self.db.execute(
            select(Comment)
            .options(selectinload(Comment.author))
            .where(Comment.id == comment_id)
        )
        comment = result.scalars().first()

        return comment

    async def get_by_post_id(
        self, post_id: int, skip: int, limit: int
    ) -> Sequence[Comment]:
        result = await self.db.execute(
            select(Comment)
            .options(
                selectinload(Comment.author),
                selectinload(Comment.replies).selectinload(Comment.author),
            )
            .where(Comment.post_id == post_id, Comment.parent_id.is_(None))
            .offset(skip)
            .limit(limit)
        )

        comments = result.scalars().all()

        return comments

    async def update(self, comment: Comment, update_data: dict[str, Any]) -> Comment:
        for field, value in update_data.items():
            setattr(comment, field, value)

        await self.db.commit()
        await self.db.refresh(comment, attribute_names=["author", "replies"])

        return comment

    async def delete(self, comment: Comment) -> None:
        await self.db.delete(comment)
        await self.db.commit()

    async def count(self, post_id: int) -> int:
        result_count = await self.db.execute(
            select(func.count())
            .select_from(Comment)
            .where(Comment.post_id == post_id, Comment.parent_id.is_(None))
        )
        total = result_count.scalar() or 0

        return total
