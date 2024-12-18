import os
from os.path import dirname

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = dirname(dirname(dirname(os.path.abspath(__file__))))
DEFAULT_ENV_FILE = os.path.join(BASE_DIR, "default.env")

env_file = os.getenv("ENV_FILE", DEFAULT_ENV_FILE)
load_dotenv(env_file)


class AuthSettings(BaseSettings):
    access_token_expire_minutes: int = 15
    secret_key: str = 'super_secret'
    sign_algorythm: str = 'HS256'


class RedisSettings(BaseSettings):
    url: str = 'redis://redis:6379/0'
    game_session_ttl: int = 3600


class AppConfig(BaseSettings):
    debug: bool = False
    database_url: str = 'postgresql+asyncpg://app_user:app_password@db/production_database'
    auth: AuthSettings = AuthSettings()
    expired_sessions_timeout: int = 600
    redis: RedisSettings = RedisSettings()
    internal_token: str = 'secret_token'

    class Config:
        env_nested_delimiter = "__"


app_config = AppConfig()
