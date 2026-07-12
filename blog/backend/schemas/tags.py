from pydantic import BaseModel, ConfigDict, Field


class TagBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)


class TagResponse(TagBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class PaginatedTagsResponse(BaseModel):
    tags: list[TagResponse]
    total: int
    skip: int
    limit: int
    has_more: bool
