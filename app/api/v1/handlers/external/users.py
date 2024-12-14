from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.api.v1.dependencies import get_auth_service
from app.api.v1.schemas.users import UserCreate
from app.api.v1.services.auth_service import AuthService
from app.exceptions import UserNotFound, Unauthorized

users_router = APIRouter()


@users_router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), auth_service: AuthService = Depends(get_auth_service)
):
    try:
        access_token = await auth_service.create_token(form_data.username, form_data.password)
    except UserNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Unauthorized:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": access_token, "token_type": "bearer"}


@users_router.post("/register")
async def register_user(user: UserCreate, auth_service: AuthService = Depends(get_auth_service)):
    try:
        await auth_service.register_user(user)
    except ValueError:
        raise HTTPException(status_code=400, detail="Email or username already registered")
    else:
        return {"message": "User registered successfully"}
