import logging

from app.core.config import app_config

logging.basicConfig(
    level=logging.INFO if not app_config.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

session_logger = logging.getLogger("SessionService")
