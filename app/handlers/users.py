import asyncio
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.config import app_config
from app.database.dao.UsersDAO import UsersDAO
from app.database.utils import get_db
from app.handlers.schemas import UserCreate
from app.handlers.utils import oauth2_scheme, verify_password, create_access_token

users_router = APIRouter()


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    dao = UsersDAO(db)
    try:
        payload = jwt.decode(token, app_config.secret_key, algorithms=[app_config.sign_algorythm])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = await dao.get_user(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def authenticate_user(username: str, password: str, db: AsyncSession):
    dao = UsersDAO(db)
    user = await dao.get_user(username)
    if not user:
        await asyncio.sleep(0.5)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(password, user.hashed_password):
        await asyncio.sleep(0.5)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@users_router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(form_data.username, form_data.password, db)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=app_config.access_token_expire_minutes),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@users_router.post("/register")
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    dao = UsersDAO(db)
    try:
        await dao.register_user(user)
    except ValueError:
        raise HTTPException(status_code=400, detail="Email or username already registered")
    else:
        return {"message": "User registered successfully"}
