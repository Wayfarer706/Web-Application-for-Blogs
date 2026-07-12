from fastapi import HTTPException, status

from models.category import Category
from repositories.category_repository import CategoryRepository
from schemas.categories import (
    CategoryResponse,
    CategoryUpdate,
    PaginatedCategoriesResponse,
)


class CategoryService:
    def __init__(self, category_repo: CategoryRepository) -> None:
        self.category_repo = category_repo

    async def create_category(self, name: str) -> Category:
        category = await self.category_repo.get_by_name(name)

        if category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category already exists",
            )

        return await self.category_repo.create(name)

    async def get_category(self, category_id: int) -> Category:
        category = await self.category_repo.get_by_id(category_id)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

        return category

    async def get_categories(
        self, skip: int, limit: int
    ) -> PaginatedCategoriesResponse:
        total_count = await self.category_repo.count()
        categories = await self.category_repo.get_paginated(skip, limit)

        has_more = skip + len(categories) < total_count

        return PaginatedCategoriesResponse(
            categories=[
                CategoryResponse.model_validate(category) for category in categories
            ],
            total=total_count,
            skip=skip,
            limit=limit,
            has_more=has_more,
        )

    async def update_category(
        self, category_id: int, category_data: CategoryUpdate
    ) -> Category:
        category = await self.category_repo.get_by_id(category_id)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        if category_data.name is not None and category_data.name != category.name:
            existing_category_by_name = await self.category_repo.get_by_name(
                category_data.name
            )

            if existing_category_by_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category already exists",
                )

        update_data = category_data.model_dump(exclude_unset=True)
        return await self.category_repo.update(category, update_data)

    async def delete_category(self, category_id: int) -> None:
        category = await self.category_repo.get_by_id(category_id)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

        await self.category_repo.delete(category)
