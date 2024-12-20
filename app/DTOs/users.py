from app.core.password_utils import get_password_hash
from app.handlers.api.v1.schemas.users import UserCreate


class UserDTO:
    def __init__(self, username: str, email: str, hashed_password: str, full_name: str):
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.full_name = full_name

    @staticmethod
    def create_from_schema(user_create: UserCreate) -> "UserDTO":
        return UserDTO(
            username=user_create.username,
            email=user_create.email,
            hashed_password=get_password_hash(user_create.password),
            full_name=user_create.full_name,
        )
