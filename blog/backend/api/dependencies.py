from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth import CurrentUser
from database import get_db
from enums import UserRole
from models.user import User
from repositories.auth_repository import AuthRepository
from repositories.category_repository import CategoryRepository
from repositories.comment_repository import CommentRepository
from repositories.post_repository import PostRepository
from repositories.tag_repository import TagRepository
from repositories.user_repository import UserRepository
from services.category_service import CategoryService
from services.comment_service import CommentService
from services.post_service import PostService
from services.tag_service import TagService
from services.user_service import UserService


def get_post_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> PostRepository:
    return PostRepository(db)


def get_user_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> UserRepository:
    return UserRepository(db)


def get_auth_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> AuthRepository:
    return AuthRepository(db)


def get_category_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CategoryRepository:
    return CategoryRepository(db)


def get_tag_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> TagRepository:
    return TagRepository(db)


def get_comment_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CommentRepository:
    return CommentRepository(db)


def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    post_repo: Annotated[PostRepository, Depends(get_post_repository)],
    auth_repo: Annotated[AuthRepository, Depends(get_auth_repository)],
) -> UserService:
    return UserService(user_repo, post_repo, auth_repo)


def get_post_service(
    post_repo: Annotated[PostRepository, Depends(get_post_repository)],
    category_repo: Annotated[CategoryRepository, Depends(get_category_repository)],
    tag_repo: Annotated[TagRepository, Depends(get_tag_repository)],
) -> PostService:
    return PostService(post_repo, category_repo, tag_repo)


def get_category_service(
    category_repo: Annotated[CategoryRepository, Depends(get_category_repository)],
) -> CategoryService:
    return CategoryService(category_repo)


def get_tag_service(
    tag_repo: Annotated[TagRepository, Depends(get_tag_repository)],
) -> TagService:
    return TagService(tag_repo)


def get_comment_service(
    comment_repo: Annotated[CommentRepository, Depends(get_comment_repository)],
    post_repo: Annotated[PostRepository, Depends(get_post_repository)],
) -> CommentService:
    return CommentService(comment_repo, post_repo)


async def get_current_admin_user(current_user: CurrentUser) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )

    return current_user
