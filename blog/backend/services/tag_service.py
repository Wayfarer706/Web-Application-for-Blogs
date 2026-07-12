from fastapi import HTTPException, status

from models.tag import Tag
from repositories.tag_repository import TagRepository
from schemas.tags import (
    PaginatedTagsResponse,
    TagResponse,
    TagUpdate,
)


class TagService:
    def __init__(self, tag_repo: TagRepository) -> None:
        self.tag_repo = tag_repo

    async def create_tag(self, name: str) -> Tag:
        tag = await self.tag_repo.get_by_name(name)

        if tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag already exists",
            )

        return await self.tag_repo.create(name)

    async def get_tag(self, tag_id: int) -> Tag:
        tag = await self.tag_repo.get_by_id(tag_id)

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
            )

        return tag

    async def get_tags(self, skip: int, limit: int) -> PaginatedTagsResponse:
        total_count = await self.tag_repo.count()
        tags = await self.tag_repo.get_paginated(skip, limit)

        has_more = skip + len(tags) < total_count

        return PaginatedTagsResponse(
            tags=[TagResponse.model_validate(tag) for tag in tags],
            total=total_count,
            skip=skip,
            limit=limit,
            has_more=has_more,
        )

    async def update_tag(self, tag_id: int, tag_data: TagUpdate) -> Tag:
        tag = await self.tag_repo.get_by_id(tag_id)

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found",
            )

        if tag_data.name is not None and tag_data.name != tag.name:
            existing_tag_by_name = await self.tag_repo.get_by_name(tag_data.name)

            if existing_tag_by_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tag already exists",
                )

        update_data = tag_data.model_dump(exclude_unset=True)
        return await self.tag_repo.update(tag, update_data)

    async def delete_tag(self, tag_id: int) -> None:
        tag = await self.tag_repo.get_by_id(tag_id)

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
            )

        await self.tag_repo.delete(tag)
