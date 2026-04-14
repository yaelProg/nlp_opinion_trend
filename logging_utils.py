from __future__ import annotations
from loguru import logger

import sys


def setup_logger() -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    )
