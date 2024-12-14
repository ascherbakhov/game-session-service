from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext


def get_password_hash(password):
    return pwd_context.hash(password)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
