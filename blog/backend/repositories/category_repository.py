from collections.abc import Sequence
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.category import Category


class CategoryRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, category_id: int) -> Category | None:
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        category = result.scalars().first()

        return category

    async def get_by_name(self, name: str) -> Category | None:
        result = await self.db.execute(select(Category).where(Category.name == name))
        category = result.scalars().first()

        return category

    async def get_paginated(self, skip: int, limit: int) -> Sequence[Category]:
        result = await self.db.execute(select(Category).offset(skip).limit(limit))
        categories = result.scalars().all()

        return categories

    async def create(self, name: str) -> Category:
        new_category = Category(name=name)

        self.db.add(new_category)
        await self.db.commit()
        await self.db.refresh(new_category)

        return new_category

    async def update(self, category: Category, update_data: dict[str, Any]) -> Category:
        for field, value in update_data.items():
            setattr(category, field, value)

        await self.db.commit()
        await self.db.refresh(category)

        return category

    async def delete(self, category: Category) -> None:
        await self.db.delete(category)
        await self.db.commit()

    async def count(self) -> int:
        result_count = await self.db.execute(select(func.count()).select_from(Category))
        total = result_count.scalar() or 0

        return total
