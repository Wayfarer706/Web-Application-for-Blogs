from fastapi import HTTPException, status

from models.comment import Comment
from repositories.comment_repository import CommentRepository
from repositories.post_repository import PostRepository
from schemas.comments import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
    PaginatedCommentsResponse,
)


class CommentService:
    def __init__(
        self, comment_repo: CommentRepository, post_repo: PostRepository
    ) -> None:
        self.comment_repo = comment_repo
        self.post_repo = post_repo

    async def create_comment(
        self, comment_data: CommentCreate, user_id: int
    ) -> Comment:
        post = await self.post_repo.get_by_id(comment_data.post_id)

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )

        if comment_data.parent_id:
            parent_comment = await self.comment_repo.get_by_id(comment_data.parent_id)

            if not parent_comment or parent_comment.post_id != comment_data.post_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent comment not found",
                )

        return await self.comment_repo.create(
            user_id, comment_data.post_id, comment_data.content, comment_data.parent_id
        )

    async def get_post_comments(
        self, post_id: int, skip: int, limit: int
    ) -> PaginatedCommentsResponse:
        post = await self.post_repo.get_by_id(post_id)

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )

        total_count = await self.comment_repo.count(post_id)
        comments = await self.comment_repo.get_by_post_id(post_id, skip, limit)

        has_more = skip + len(comments) < total_count

        return PaginatedCommentsResponse(
            comments=[CommentResponse.model_validate(comment) for comment in comments],
            total=total_count,
            skip=skip,
            limit=limit,
            has_more=has_more,
        )

    async def update_comment(
        self, comment_id: int, user_id: int, comment_data: CommentUpdate
    ) -> Comment:
        comment = await self._get_comment_and_verify_owner(comment_id, user_id)
        update_data = comment_data.model_dump(exclude_unset=True)

        return await self.comment_repo.update(comment, update_data)

    async def delete_comment(self, comment_id: int, user_id: int) -> None:
        comment = await self._get_comment_and_verify_owner(comment_id, user_id)
        return await self.comment_repo.delete(comment)

    async def _get_comment_and_verify_owner(
        self, comment_id: int, user_id: int
    ) -> Comment:
        comment = await self.comment_repo.get_by_id(comment_id)

        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found",
            )

        if comment.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this comment",
            )

        return comment
