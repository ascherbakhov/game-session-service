import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ENV_FILE = os.path.join(BASE_DIR, "default.env")

env_file = os.getenv("ENV_FILE", DEFAULT_ENV_FILE)
load_dotenv(env_file)


class Config(BaseSettings):
    debug: bool
    database_url: str
    access_token_expire_minutes: int
    secret_key: str


app_config = Config()
