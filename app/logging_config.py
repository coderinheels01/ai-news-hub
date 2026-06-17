import logging
import os


def configure_logging() -> None:
    """Configure logging for the application.

    Call this once at the application entry point. Subsequent calls are no-ops
    because basicConfig() only applies when no handlers are already set on the
    root logger.
    """
    log_level_name: str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level: int = getattr(logging, log_level_name, logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
