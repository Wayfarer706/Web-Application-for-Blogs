from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from api.dependencies import get_category_service, get_current_admin_user
from schemas.categories import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    PaginatedCategoriesResponse,
)
from services.category_service import CategoryService

router = APIRouter()


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    category_service: Annotated[CategoryService, Depends(get_category_service)],
):
    return await category_service.get_category(category_id)


@router.get("", response_model=PaginatedCategoriesResponse)
async def get_categories(
    category_service: Annotated[CategoryService, Depends(get_category_service)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    return await category_service.get_categories(skip, limit)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin_user)],
)
async def create_category(
    category: CategoryCreate,
    category_service: Annotated[CategoryService, Depends(get_category_service)],
):
    return await category_service.create_category(category.name)


@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
    dependencies=[Depends(get_current_admin_user)],
)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    category_service: Annotated[CategoryService, Depends(get_category_service)],
):
    return await category_service.update_category(category_id, category_data)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin_user)],
)
async def delete_category(
    category_id: int,
    category_service: Annotated[CategoryService, Depends(get_category_service)],
):
    await category_service.delete_category(category_id)
