import logging
import os
import sys
from datetime import datetime

from . import settings


class Logger:
    """
    Singleton logger specifically for SLM_Server.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_internal_logger()
        return cls._instance

    def _setup_internal_logger(self):
        """Set up the logger with file and console handlers."""
        log_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"slm_server_{timestamp}.log")

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_format)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
        console_format = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(console_format)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    @classmethod
    def info(cls, msg: object, *args: object) -> None:
        """
        Log an info message.
        """
        cls().logger.info(msg, *args)

    @classmethod
    def debug(cls, msg: object, *args: object) -> None:
        """
        Log a debug message.
        """
        cls().logger.debug(msg, *args)

    @classmethod
    def warning(cls, msg: object, *args: object) -> None:
        """
        Log a warning message.
        """
        cls().logger.warning(msg, *args)

    @classmethod
    def error(cls, msg: object, *args: object) -> None:
        """
        Log an error message.
        """
        cls().logger.error(msg, *args)

    @classmethod
    def exception(cls, msg: object, *args: object) -> None:
        """
        Log an exception message.
        """
        cls().logger.exception(msg, *args)
