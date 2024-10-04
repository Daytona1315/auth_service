from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import models
from src.database.engine import get_async_session
from src.schemas.auth_schema import BaseUser


class UtilitiesService:
    """Service with various helpful methods"""

    def __init__(self, async_session: AsyncSession = Depends(get_async_session)):
        self.async_session = async_session

    # GET ALL USERS METHOD ----------
    async def get_users(self):
        async with self.async_session as session:

            # Fetch the database and get all users
            result = await session.execute(select(models.User))
            users = result.scalars().all()

            # Return a list of users according to the model BaseUser
            return [BaseUser.model_validate(user) for user in users]
