from collections.abc import Sequence
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.tag import Tag


class TagRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, tag_id: int) -> Tag | None:
        result = await self.db.execute(select(Tag).where(Tag.id == tag_id))
        tag = result.scalars().first()

        return tag

    async def get_by_ids(self, tag_ids: list[int]) -> list[Tag]:
        if not tag_ids:
            return []

        result = await self.db.execute(select(Tag).where(Tag.id.in_(tag_ids)))
        return list(result.scalars().all())

    async def get_by_name(self, name: str) -> Tag | None:
        result = await self.db.execute(select(Tag).where(Tag.name == name))
        tag = result.scalars().first()

        return tag

    async def get_paginated(self, skip: int, limit: int) -> Sequence[Tag]:
        result = await self.db.execute(select(Tag).offset(skip).limit(limit))
        tags = result.scalars().all()

        return tags

    async def create(self, name: str) -> Tag:
        new_tag = Tag(name=name)

        self.db.add(new_tag)
        await self.db.commit()
        await self.db.refresh(new_tag)

        return new_tag

    async def update(self, tag: Tag, update_data: dict[str, Any]) -> Tag:
        for field, value in update_data.items():
            setattr(tag, field, value)

        await self.db.commit()
        await self.db.refresh(tag)

        return tag

    async def delete(self, tag: Tag) -> None:
        await self.db.delete(tag)
        await self.db.commit()

    async def count(self) -> int:
        result_count = await self.db.execute(select(func.count()).select_from(Tag))
        total = result_count.scalar() or 0

        return total
