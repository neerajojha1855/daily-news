"""
Structured logging configuration.
"""
import logging
import sys
from typing import Any

from app.core.config import get_settings

settings = get_settings()

try:
    import structlog

    def setup_logging() -> None:
        """Configure structured logging with structlog."""
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=logging.INFO if not settings.DEBUG else logging.DEBUG,
        )

        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso", utc=True),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
                if settings.is_production
                else structlog.dev.ConsoleRenderer(),
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    def get_logger(name: str):
        return structlog.get_logger(name)

    def bind_request_context(request_id: str, **kwargs: Any) -> None:
        structlog.contextvars.bind_contextvars(request_id=request_id, **kwargs)

    def clear_request_context() -> None:
        structlog.contextvars.clear_contextvars()

except ImportError:
    def setup_logging() -> None:
        logging.basicConfig(
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            stream=sys.stdout,
            level=logging.INFO if not settings.DEBUG else logging.DEBUG,
        )

    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)

    def bind_request_context(request_id: str, **kwargs: Any) -> None:
        pass

    def clear_request_context() -> None:
        pass