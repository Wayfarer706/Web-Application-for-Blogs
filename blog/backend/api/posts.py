from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

import models as models
from api.dependencies import get_post_service
from auth import CurrentUser
from schemas.posts import PaginatedPostsResponse, PostCreate, PostResponse, PostUpdate
from services.post_service import PostService

router = APIRouter()


@router.get("", response_model=PaginatedPostsResponse)
async def get_posts(
    post_service: Annotated[PostService, Depends(get_post_service)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    return await post_service.get_posts(skip, limit)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    post_service: Annotated[PostService, Depends(get_post_service)],
):
    return await post_service.get_post(post_id)


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    post: PostCreate,
    current_user: CurrentUser,
    post_service: Annotated[PostService, Depends(get_post_service)],
):
    return await post_service.create_post(post, current_user.id)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post_full(
    post_id: int,
    post_data: PostCreate,
    current_user: CurrentUser,
    post_service: Annotated[PostService, Depends(get_post_service)],
):
    return await post_service.update_post_full(post_id, current_user.id, post_data)


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post_partial(
    post_id: int,
    post_data: PostUpdate,
    current_user: CurrentUser,
    post_service: Annotated[PostService, Depends(get_post_service)],
):
    return await post_service.update_post_partial(post_id, current_user.id, post_data)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: CurrentUser,
    post_service: Annotated[PostService, Depends(get_post_service)],
):
    await post_service.delete_post(post_id, current_user.id)
