from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.tables.User import User
from app.handlers.schemas import UserCreate
from app.handlers.utils import get_password_hash


class UsersDAO:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_user(self, username):
        result = await self.db_session.execute(select(User).where(User.username == username))
        user = result.scalar()
        return user

    async def register_user(self, user: UserCreate):
        hashed_password = get_password_hash(user.password)
        new_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            full_name=user.full_name,
        )

        self.db_session.add(new_user)

        try:
            await self.db_session.commit()
            return new_user
        except IntegrityError:
            await self.db_session.rollback()
            raise ValueError("Username or email already exists")