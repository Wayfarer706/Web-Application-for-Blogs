from sqlalchemy import delete as sql_delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models as models


class AuthRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, reset_token: models.PasswordResetToken) -> None:
        self.db.add(reset_token)
        await self.db.commit()

    async def delete_tokens_for_user(self, user_id: int) -> None:
        await self.db.execute(
            sql_delete(models.PasswordResetToken).where(
                models.PasswordResetToken.user_id == user_id,
            ),
        )
        await self.db.commit()

    async def get_reset_token(
        self, token_hash: str
    ) -> models.PasswordResetToken | None:
        result = await self.db.execute(
            select(models.PasswordResetToken).where(
                models.PasswordResetToken.token_hash == token_hash,
            ),
        )
        reset_token = result.scalars().first()

        return reset_token

    async def delete_reset_token(self, reset_token: models.PasswordResetToken) -> None:
        await self.db.delete(reset_token)
        await self.db.commit()
