from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from api.dependencies import get_current_admin_user, get_tag_service
from schemas.tags import (
    PaginatedTagsResponse,
    TagCreate,
    TagResponse,
    TagUpdate,
)
from services.tag_service import TagService

router = APIRouter()


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: int,
    tag_service: Annotated[TagService, Depends(get_tag_service)],
):
    return await tag_service.get_tag(tag_id)


@router.get("", response_model=PaginatedTagsResponse)
async def get_tags(
    tag_service: Annotated[TagService, Depends(get_tag_service)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    return await tag_service.get_tags(skip, limit)


@router.post(
    "",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin_user)],
)
async def create_tag(
    tag: TagCreate,
    tag_service: Annotated[TagService, Depends(get_tag_service)],
):
    return await tag_service.create_tag(tag.name)


@router.patch(
    "/{tag_id}",
    response_model=TagResponse,
    dependencies=[Depends(get_current_admin_user)],
)
async def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    tag_service: Annotated[TagService, Depends(get_tag_service)],
):
    return await tag_service.update_tag(tag_id, tag_data)


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin_user)],
)
async def delete_tag(
    tag_id: int,
    tag_service: Annotated[TagService, Depends(get_tag_service)],
):
    await tag_service.delete_tag(tag_id)
