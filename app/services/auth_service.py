import asyncio
from datetime import timedelta, datetime, UTC
from typing import Optional

from jose import jwt, JWTError

from app.core.config import AuthSettings
from app.core.password_utils import get_password_hash, verify_password
from app.DTOs.users import UserCreate
from app.database.dao.users_dao import UsersDAO
from app.database.tables.models import User
from app.exceptions import UserNotFound, Unauthorized


class AuthService:
    def __init__(self, users_dao: UsersDAO, authConfig: AuthSettings):
        self.__users_dao = users_dao
        self.__authSettings = authConfig

    async def get_user(self, username: str) -> User:
        return await self.__users_dao.get_user(username)

    async def register_user(self, user: UserCreate) -> User:
        hashed_password = get_password_hash(user.password)
        return await self.__users_dao.create_user(user, hashed_password)

    async def create_token(self, username: str, password: str) -> str:
        user = await self.authenticate_user(username, password)
        access_token = self.__create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=self.__authSettings.access_token_expire_minutes),
        )
        return access_token

    async def authenticate_user(self, username: str, password: str) -> User:
        user = await self.__users_dao.get_user(username)
        if not user:
            await asyncio.sleep(0.5)
            raise UserNotFound()
        if not verify_password(password, user.hashed_password):
            await asyncio.sleep(0.5)
            raise Unauthorized()
        return user

    async def get_user_by_token(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(token, self.__authSettings.secret_key, algorithms=[self.__authSettings.sign_algorythm])
            username: str = payload.get("sub")
            if not username:
                return None
            user = await self.__users_dao.get_user(username)
            return user
        except JWTError:
            return None

    def __create_access_token(self, data: dict, expires_delta: Optional[timedelta]) -> str:
        to_encode = data.copy()
        expire = datetime.now(UTC) + expires_delta
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.__authSettings.secret_key, algorithm=self.__authSettings.sign_algorythm)
