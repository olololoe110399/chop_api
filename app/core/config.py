"""Define config for project."""
from __future__ import annotations
import streamlit as st

import logging
import sys

from loguru import logger

from app.core.logging import InterceptHandler

DEBUG: bool = st.secrets["debug"]
OPEN_API_KEY: str = st.secrets["open_api_key"]

# logging configuration
LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
LOGGERS = ("uvicorn.asgi", "uvicorn.access")

logging.getLogger().handlers = [InterceptHandler()]
for logger_name in LOGGERS:
    logging_logger = logging.getLogger(logger_name)
    logging_logger.handlers = [InterceptHandler(level=LOGGING_LEVEL)]

logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])
