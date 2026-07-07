from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from repositories.auth_repository import AuthRepository
from repositories.post_repository import PostRepository
from repositories.user_repository import UserRepository
from services.post_service import PostService
from services.user_service import UserService


def get_post_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> PostRepository:
    return PostRepository(db)


def get_post_service(
    repo: Annotated[PostRepository, Depends(get_post_repository)],
) -> PostService:
    return PostService(repo)


def get_user_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> UserRepository:
    return UserRepository(db)


def get_auth_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> AuthRepository:
    return AuthRepository(db)


def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    post_repo: Annotated[PostRepository, Depends(get_post_repository)],
    auth_repo: Annotated[AuthRepository, Depends(get_auth_repository)],
) -> UserService:
    return UserService(user_repo, post_repo, auth_repo)
