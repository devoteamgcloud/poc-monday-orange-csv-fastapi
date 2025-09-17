import logging
from typing import Any

from src.config import settings


class Singleton(type):
    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Logger(metaclass=Singleton):
    def __init__(self) -> None:
        self._logger = None
        self._logger = logging.getLogger(settings.log_name)

        # Prevent the logger from propagating messages to the root logger
        self._logger.propagate = False

        # Clear any existing handlers to avoid duplicates
        if self._logger.handlers:
            self._logger.handlers.clear()

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        # Set the custom formatter for the console handler
        console_handler.setFormatter(logging.Formatter(settings.log_format))

        self._logger.addHandler(console_handler)
        self._logger.setLevel(logging.DEBUG)

    @property
    def logger(self) -> Any:
        return self._logger


logger = Logger().logger
