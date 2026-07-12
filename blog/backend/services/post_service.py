from fastapi import HTTPException, status

from models.post import Post
from models.tag import Tag
from repositories.category_repository import CategoryRepository
from repositories.post_repository import PostRepository
from repositories.tag_repository import TagRepository
from schemas.posts import PaginatedPostsResponse, PostCreate, PostResponse, PostUpdate


class PostService:
    def __init__(
        self,
        post_repo: PostRepository,
        category_repo: CategoryRepository,
        tag_repo: TagRepository,
    ) -> None:
        self.post_repo = post_repo
        self.category_repo = category_repo
        self.tag_repo = tag_repo

    async def create_post(self, post_data: PostCreate, user_id: int) -> Post:
        category = await self.category_repo.get_by_id(post_data.category_id)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

        tags: list[Tag] = []
        if post_data.tag_ids:
            tags = await self.tag_repo.get_by_ids(post_data.tag_ids)

            if len(tags) != len(set(post_data.tag_ids)):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
                )

        return await self.post_repo.create(
            title=post_data.title,
            content=post_data.content,
            user_id=user_id,
            category_id=post_data.category_id,
            tags=tags,
        )

    async def get_post(self, post_id: int) -> Post:
        post = await self.post_repo.get_post_with_author(post_id)

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )

        return post

    async def get_posts(self, skip: int, limit: int) -> PaginatedPostsResponse:
        total_count = await self.post_repo.count()
        posts = await self.post_repo.get_paginated(skip, limit)

        has_more = skip + len(posts) < total_count

        return PaginatedPostsResponse(
            posts=[PostResponse.model_validate(post) for post in posts],
            total=total_count,
            skip=skip,
            limit=limit,
            has_more=has_more,
        )

    async def update_post_full(
        self, post_id: int, user_id: int, post_data: PostCreate
    ) -> Post:
        post = await self._get_post_and_verify_owner(post_id, user_id)
        update_data = post_data.model_dump()

        return await self.post_repo.update(post, update_data)

    async def update_post_partial(
        self, post_id: int, user_id: int, post_data: PostUpdate
    ) -> Post:
        post = await self._get_post_and_verify_owner(post_id, user_id)
        update_data = post_data.model_dump(exclude_unset=True)

        return await self.post_repo.update(post, update_data)

    async def delete_post(self, post_id: int, user_id: int) -> None:
        post = await self._get_post_and_verify_owner(post_id, user_id)
        await self.post_repo.delete(post)

    async def _get_post_and_verify_owner(self, post_id: int, user_id: int) -> Post:
        post = await self.post_repo.get_by_id(post_id)

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )

        if post.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this post",
            )

        return post
