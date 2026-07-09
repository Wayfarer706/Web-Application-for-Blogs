from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from schemas.users import UserPublic


class CommentBase(BaseModel):
    content: str = Field(min_length=1)


class CommentCreate(CommentBase):
    post_id: int
    parent_id: int | None


class CommentUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1)


class CommentResponse(CommentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    post_id: int
    parent_id: int | None
    author: UserPublic
    replies: list[CommentResponse] = Field(default=[])
