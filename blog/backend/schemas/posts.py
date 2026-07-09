from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from schemas.categories import CategoryResponse
from schemas.comments import CommentResponse
from schemas.tags import TagResponse
from schemas.users import UserPublic


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)


class PostCreate(PostBase):
    category_id: int
    tag_ids: list[int] = Field(default_factory=lambda: [])


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, min_length=1)
    category_id: int | None = Field(default=None)
    tag_ids: list[int] | None = Field(default=None)


class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date_posted: datetime
    author: UserPublic
    category: CategoryResponse
    tags: list[TagResponse]
    comments: list[CommentResponse] = Field(default=[])


class PaginatedPostsResponse(BaseModel):
    posts: list[PostResponse]
    total: int
    skip: int
    limit: int
    has_more: bool
