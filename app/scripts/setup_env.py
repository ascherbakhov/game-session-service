import os
from os.path import dirname
import shutil


BASE_DIR = dirname(dirname(dirname(os.path.abspath(__file__))))
DEFAULT_ENV_FILE = os.path.join(BASE_DIR, ".env")
EXAMPLE_ENV_FILE = os.path.join(BASE_DIR, "example.env")


def setup_env():
    if not os.path.exists(EXAMPLE_ENV_FILE):
        print(f"{EXAMPLE_ENV_FILE} file not found. Please check the repository.")
        return

    if not os.path.exists(DEFAULT_ENV_FILE):
        shutil.copy(EXAMPLE_ENV_FILE, DEFAULT_ENV_FILE)
        print(f"{DEFAULT_ENV_FILE} created from {EXAMPLE_ENV_FILE}.")
    else:
        print(f"{DEFAULT_ENV_FILE} already exists. No changes made.")
