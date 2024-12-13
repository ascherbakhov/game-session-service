import os
from os.path import dirname

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = dirname(dirname(dirname(os.path.abspath(__file__))))
DEFAULT_ENV_FILE = os.path.join(BASE_DIR, "default.env")

env_file = os.getenv("ENV_FILE", DEFAULT_ENV_FILE)
load_dotenv(env_file)


class Config(BaseSettings):
    debug: bool
    database_url: str
    access_token_expire_minutes: int
    secret_key: str
    sign_algorythm: str
    expired_sessions_timeout: int
    redis_url: str
    internal_token: str


app_config = Config()
