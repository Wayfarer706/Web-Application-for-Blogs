from datetime import UTC, datetime, timedelta

from botocore.exceptions import ClientError
from fastapi import BackgroundTasks, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm
from PIL import UnidentifiedImageError
from starlette.concurrency import run_in_threadpool

import models as models
from auth import (
    create_access_token,
    generate_reset_token,
    hash_password,
    hash_reset_token,
    verify_password,
)
from config import settings
from email_utils import send_password_reset_email
from image_utils import (
    delete_profile_image,
    process_profile_image,
    upload_profile_image,
)
from repositories.auth_repository import AuthRepository
from repositories.post_repository import PostRepository
from repositories.user_repository import UserRepository
from schemas.auth import ChangePasswordRequest, Token
from schemas.posts import PaginatedPostsResponse, PostResponse
from schemas.users import UserCreate, UserUpdate


class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        post_repo: PostRepository,
        auth_repo: AuthRepository,
    ) -> None:
        self.user_repo = user_repo
        self.post_repo = post_repo
        self.auth_repo = auth_repo

    async def login_for_access_token(
        self, form_data: OAuth2PasswordRequestForm
    ) -> Token:
        user = await self.user_repo.get_by_email(form_data.username.lower())

        if not user or not verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires,
        )

        return Token(access_token=access_token, token_type="bearer")

    async def create_user(self, user: UserCreate) -> models.User:
        result = await self.user_repo.get_by_username(user.username)

        if result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

        result = await self.user_repo.get_by_email(user.email)

        if result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
            )

        return await self.user_repo.create(user.username, user.email, user.password)

    async def get_user(self, user_id: int) -> models.User:
        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return user

    async def get_user_posts(
        self, user_id: int, skip: int, limit: int
    ) -> PaginatedPostsResponse:
        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        user_posts_count = await self.post_repo.count_user_posts(user_id)

        user_posts = await self.post_repo.get_user_posts_paginated(user_id, skip, limit)

        has_more = skip + len(user_posts) < user_posts_count

        return PaginatedPostsResponse(
            posts=[PostResponse.model_validate(post) for post in user_posts],
            total=user_posts_count,
            skip=skip,
            limit=limit,
            has_more=has_more,
        )

    async def update_user(
        self,
        user_id: int,
        user_update: UserUpdate,
        current_user: models.User,
    ) -> models.User:
        if user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this user",
            )

        if (
            user_update.username is not None
            and user_update.username != current_user.username
        ):
            existing_user_by_username = await self.user_repo.get_by_username(
                user_update.username
            )

            if existing_user_by_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists",
                )

        if user_update.email is not None and user_update.email != current_user.email:
            existing_user_by_email = await self.user_repo.get_by_email(
                user_update.email
            )

            if existing_user_by_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists",
                )

        update_data = user_update.model_dump(exclude_unset=True)

        return await self.user_repo.update(current_user, update_data)

    async def upload_profile_picture(
        self, user_id: int, file: UploadFile, current_user: models.User
    ) -> models.User:
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this user's profile picture",
            )

        content = await file.read()

        if len(content) > settings.max_upload_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size is {settings.max_upload_size_bytes // (1024 * 1024)}MB",
            )

        try:
            processed_bytes, new_filename = await run_in_threadpool(
                process_profile_image, content
            )
        except UnidentifiedImageError as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid imagefile. Please upload a valid image (JPEG, PNG, GIF, WebP)",
            ) from err

        # Upload to S3 (also runs in threadpool via async wrapper)
        try:
            await upload_profile_image(processed_bytes, new_filename)
        except ClientError as err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload image. Please try again.",
            ) from err

        old_filename = current_user.image_file

        await self.user_repo.update_profile_picture(current_user, new_filename)

        if old_filename:
            await delete_profile_image(old_filename)

        return current_user

    async def delete_user(self, user_id: int, current_user_id: int) -> None:
        if user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this user",
            )

        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        old_filename = user.image_file

        await self.user_repo.delete(user)

        if old_filename:
            await delete_profile_image(old_filename)

    async def delete_user_picture(
        self, user_id: int, current_user: models.User
    ) -> models.User:
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this user's profile picture",
            )

        old_filename = current_user.image_file

        if old_filename is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No profile picture to delete",
            )

        await self.user_repo.delete_profile_picture(current_user)

        await delete_profile_image(old_filename)

        return current_user

    async def reset_password(self, token: str, new_password: str) -> dict[str, str]:
        token_hash = hash_reset_token(token)

        reset_token = await self.auth_repo.get_reset_token(token_hash)

        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        if reset_token.expires_at < datetime.now(UTC):
            await self.auth_repo.delete_reset_token(reset_token)

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        user = await self.user_repo.get_by_id(reset_token.user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        new_hashed_password = hash_password(new_password)
        await self.user_repo.update(user, {"password_hash": new_hashed_password})

        await self.auth_repo.delete_tokens_for_user(user.id)

        return {
            "message": "Password reset successfully. You can now log in with your new password."
        }

    async def change_password(
        self,
        user: models.User,
        password_data: ChangePasswordRequest,
    ) -> dict[str, str]:
        if not verify_password(password_data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        new_hashed_password = hash_password(password_data.new_password)
        await self.user_repo.update(user, {"password_hash": new_hashed_password})

        await self.auth_repo.delete_tokens_for_user(user.id)

        return {"message": "Password changed successfully"}

    async def forgot_password(
        self, request_email: str, background_tasks: BackgroundTasks
    ) -> dict[str, str]:
        user = await self.user_repo.get_by_email(request_email)

        if user:
            await self.auth_repo.delete_tokens_for_user(user.id)

            token = generate_reset_token()
            token_hash = hash_reset_token(token)
            expires_at = datetime.now(UTC) + timedelta(
                minutes=settings.reset_token_expire_minutes
            )

            reset_token = models.PasswordResetToken(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=expires_at,
            )

            await self.auth_repo.create(reset_token)

            background_tasks.add_task(
                send_password_reset_email,
                to_email=user.email,
                username=user.username,
                token=token,
            )

        return {
            "message": "If an account exists with this email, you will receive password reset instructions."
        }
