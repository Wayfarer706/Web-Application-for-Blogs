from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from repositories.post_repository import PostRepository
from services.post_service import PostService


def get_post_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> PostRepository:
    return PostRepository(db)


def get_post_service(
    repo: Annotated[PostRepository, Depends(get_post_repository)],
) -> PostService:
    return PostService(repo)
