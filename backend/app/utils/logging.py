from pathlib import Path

from loguru import logger


def configure_logging(level: str) -> None:
    Path("logs").mkdir(exist_ok=True)
    logger.remove()
    logger.add("logs/app.log", rotation="10 MB", retention="14 days", level=level, enqueue=True)
    logger.add(lambda message: print(message, end=""), level=level)
