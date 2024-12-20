from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.DTOs.users import UserDTO
from app.database.tables.models import User


class UsersDAO:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_user(self, username: str) -> User:
        result = await self.db_session.execute(select(User).where(User.username == username))
        user = result.scalar()
        return user

    async def create_user(self, user: UserDTO) -> User:
        new_user = User(
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
        )

        self.db_session.add(new_user)

        try:
            await self.db_session.commit()
            return new_user
        except IntegrityError:
            await self.db_session.rollback()
            raise ValueError("Username or email already exists")
