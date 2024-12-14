import asyncio
from datetime import timedelta, datetime, UTC
from typing import Optional

from jose import jwt, JWTError

from app.api.v1.handlers.external.utils import get_password_hash, pwd_context
from app.api.v1.schemas.users import UserCreate
from app.core.config import app_config
from app.exceptions import UserNotFound, Unauthorized


class AuthService:
    def __init__(self, users_dao):
        self.__users_dao = users_dao

    async def get_user(self, username):
        return await self.__users_dao.get_user(username)

    async def register_user(self, user: UserCreate):
        hashed_password = get_password_hash(user.password)
        return await self.__users_dao.create_user(user, hashed_password)

    async def create_token(self, username, password):
        user = await self.authenticate_user(username, password)
        access_token = self.__create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=app_config.access_token_expire_minutes),
        )
        return access_token

    async def authenticate_user(self, username: str, password: str):
        user = await self.__users_dao.get_user(username)
        if not user:
            await asyncio.sleep(0.5)
            raise UserNotFound()
        if not self.__verify_password(password, user.hashed_password):
            await asyncio.sleep(0.5)
            raise Unauthorized()
        return user

    async def get_user_by_token(self, token):
        try:
            payload = jwt.decode(token, app_config.secret_key, algorithms=[app_config.sign_algorythm])
            username: str = payload.get("sub")
            if not username:
                return None
            user = await self.__users_dao.get_user(username)
            return user
        except JWTError:
            return None

    def __verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def __create_access_token(self, data: dict, expires_delta: Optional[timedelta]):
        to_encode = data.copy()
        expire = datetime.now(UTC) + expires_delta
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, app_config.secret_key, algorithm=app_config.sign_algorythm)