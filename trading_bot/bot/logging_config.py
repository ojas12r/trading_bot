"""
Structured logging configuration for the trading bot.
Logs to both console (INFO+) and a rotating file (DEBUG+).
"""

import logging
import logging.handlers
import os
from pathlib import Path


LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE = LOG_DIR / "trading_bot.log"

_CONFIGURED = False


def setup_logging(log_level: str = "DEBUG") -> logging.Logger:
    """
    Configure root logger with:
      - StreamHandler  → console (INFO and above)
      - RotatingFileHandler → logs/trading_bot.log (DEBUG and above)
    """
    global _CONFIGURED
    if _CONFIGURED:
        return logging.getLogger("trading_bot")

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger("trading_bot")
    root.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler — INFO+
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)
    root.addHandler(console)

    # Rotating file handler — DEBUG+
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    _CONFIGURED = True
    root.info("Logging initialised. Log file → %s", LOG_FILE)
    return root


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the 'trading_bot' hierarchy."""
    setup_logging()
    return logging.getLogger(f"trading_bot.{name}")
