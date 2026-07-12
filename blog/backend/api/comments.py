from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.dependencies import get_comment_service
from auth import CurrentUser
from schemas.comments import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
)
from services.comment_service import CommentService

router = APIRouter()


@router.post(
    "",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    comment_data: CommentCreate,
    current_user: CurrentUser,
    comment_service: Annotated[CommentService, Depends(get_comment_service)],
):
    return await comment_service.create_comment(comment_data, current_user.id)


@router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    current_user: CurrentUser,
    comment_data: CommentUpdate,
    comment_service: Annotated[CommentService, Depends(get_comment_service)],
):
    return await comment_service.update_comment(
        comment_id, current_user.id, comment_data
    )


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user: CurrentUser,
    comment_service: Annotated[CommentService, Depends(get_comment_service)],
):
    await comment_service.delete_comment(comment_id, current_user.id)
