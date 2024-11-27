from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.tables.User import User


class UsersDAO:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_user(self, username):
        result = await self.db_session.execute(select(User).where(User.username == username))
        user = result.scalar()
        return user
