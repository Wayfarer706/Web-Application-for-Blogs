from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Query,
    UploadFile,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm

from api.dependencies import get_user_service
from auth import CurrentUser
from schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    Token,
)
from schemas.posts import PaginatedPostsResponse
from schemas.users import UserCreate, UserPrivate, UserPublic, UserUpdate
from services.user_service import UserService

router = APIRouter()


@router.post("", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate, user_service: Annotated[UserService, Depends(get_user_service)]
):
    return await user_service.create_user(user)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return await user_service.login_for_access_token(form_data)


@router.get("/me", response_model=UserPrivate)
async def get_current_user(current_user: CurrentUser):
    return current_user


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(
    user_id: int, user_service: Annotated[UserService, Depends(get_user_service)]
):
    return await user_service.get_user(user_id)


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
    request_data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return await user_service.forgot_password(request_data.email, background_tasks)


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    request_data: ResetPasswordRequest,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return await user_service.reset_password(
        request_data.token, request_data.new_password
    )


@router.patch("/me/password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: CurrentUser,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return await user_service.change_password(current_user, password_data)


@router.get("/{user_id}/posts", response_model=PaginatedPostsResponse)
async def get_user_posts(
    user_id: int,
    user_service: Annotated[UserService, Depends(get_user_service)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    return await user_service.get_user_posts(user_id, skip, limit)


@router.patch("/{user_id}", response_model=UserPrivate)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: CurrentUser,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return await user_service.update_user(user_id, user_update, current_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: CurrentUser,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return await user_service.delete_user(user_id, current_user.id)


@router.patch("/{user_id}/picture", response_model=UserPrivate)
async def upload_profile_picture(
    user_id: int,
    file: UploadFile,
    current_user: CurrentUser,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return await user_service.upload_profile_picture(user_id, file, current_user)


@router.delete("/{user_id}/picture", response_model=UserPrivate)
async def delete_user_picture(
    user_id: int,
    current_user: CurrentUser,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return await user_service.delete_user_picture(user_id, current_user)
