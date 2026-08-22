"""Python ``logging`` adapter implementing the application ``Logger`` protocol."""

from __future__ import annotations

import logging

from app.domain.protocols import Logger


class PythonLogger(Logger):
    """C# ``ConsoleLogger`` equivalent backed by the stdlib ``logging``."""

    def __init__(self, name: str = "rwparcer") -> None:
        self._logger = logging.getLogger(name)

    def debug(self, message: str) -> None:
        self._logger.debug(message)

    def info(self, message: str) -> None:
        self._logger.info(message)

    def warning(self, message: str) -> None:
        self._logger.warning(message)

    def error(self, message: str) -> None:
        self._logger.error(message)
