import os
from os.path import dirname

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = dirname(dirname(dirname(os.path.abspath(__file__))))
DEFAULT_ENV_FILE = os.path.join(BASE_DIR, "default.env")

env_file = os.getenv("ENV_FILE", DEFAULT_ENV_FILE)
load_dotenv(env_file)


class AuthSettings(BaseSettings):
    access_token_expire_minutes: int
    secret_key: str
    sign_algorythm: str


class AppConfig(BaseSettings):
    debug: bool
    database_url: str
    auth: AuthSettings
    expired_sessions_timeout: int
    redis_url: str
    game_session_redis_ttl: int
    internal_token: str

    class Config:
        env_nested_delimiter = "__"


app_config = AppConfig()
