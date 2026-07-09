from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from .post import Post
    from .user import User


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    date_posted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id"), nullable=False, index=True
    )

    parent_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id"), index=True)

    parent: Mapped[Comment | None] = relationship(
        back_populates="replies", remote_side="Comment.id"
    )

    author: Mapped[User] = relationship(back_populates="comments")

    post: Mapped[Post] = relationship(back_populates="comments")

    replies: Mapped[list[Comment]] = relationship(
        back_populates="parent", cascade="all, delete-orphan"
    )
