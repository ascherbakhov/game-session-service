from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.DTOs.users import UserDTO
from app.handlers.dependencies import get_auth_service
from app.handlers.api.v1.schemas.users import UserCreate
from app.services.auth_service import AuthService
from app.exceptions import UserNotFound, Unauthorized

auth_router = APIRouter()


@auth_router.post("/token")
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


@auth_router.post("/register")
async def register_user(user: UserCreate, auth_service: AuthService = Depends(get_auth_service)):
    try:
        user_dto = UserDTO.create_from_schema(user)
        await auth_service.register_user(user_dto)
    except ValueError:
        raise HTTPException(status_code=400, detail="Email or username already registered")
    else:
        return {"message": "User registered successfully"}
