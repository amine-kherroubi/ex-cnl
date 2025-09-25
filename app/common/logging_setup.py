from __future__ import annotations

# Standard library imports
import json
import logging
import logging.config
import sys
from datetime import datetime
from typing import Any, Dict, Final, Literal

# Local application imports
from app.config import LoggingConfig


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:

        log_entry: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.levelno <= logging.DEBUG:
            log_entry.update(
                {
                    "process": record.process,
                    "thread": record.thread,
                }
            )

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    COLORS: Final[dict[str, str]] = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET: Final[str] = "\033[0m"
    BOLD: Final[str] = "\033[1m"
    DIM: Final[str] = "\033[2m"

    def format(self, record: logging.LogRecord) -> str:
        message: str = super().format(record)

        if hasattr(sys.stderr, "isatty") and sys.stderr.isatty():
            level_color: str = self.COLORS.get(record.levelname, "")
            return (
                f"{level_color}{self.BOLD}[{record.levelname}]{self.RESET} "
                f"{self.DIM}{record.name}{self.RESET} - {message}"
            )

        return message


class LoggingSetup(object):
    @classmethod
    def configure(cls, config: LoggingConfig) -> None:
        if config.enable_file_logging:
            config.log_file.parent.mkdir(parents=True, exist_ok=True)

        logging_config: dict[str, Any] = cls._build_logging_config(config)

        logging.config.dictConfig(logging_config)

        logger: logging.Logger = logging.getLogger(__name__)
        logger.info("Logging configuration applied successfully")

        if config.enable_file_logging:
            logger.info(f"File logging enabled: {config.log_file}")
        if config.enable_console_logging:
            logger.info("Console logging enabled")

    @staticmethod
    def _build_logging_config(config: LoggingConfig) -> Dict[str, Any]:
        logging_config: Dict[str, Any] = {
            "version": 1,
            "disable_existing_loggers": config.disable_existing_loggers,
            "formatters": {},
            "handlers": {},
            "loggers": {},
            "root": {
                "level": config.level,
                "handlers": [],
            },
        }

        if config.use_json_format:
            logging_config["formatters"]["json"] = {
                "()": "app.common.logging_setup.JSONFormatter",
            }
            logging_config["formatters"]["console"] = {
                "()": "app.common.logging_setup.ColoredFormatter",
                "format": "%(asctime)s - %(message)s",
                "datefmt": "%H:%M:%S",
            }
        else:
            logging_config["formatters"]["detailed"] = {
                "format": "%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
            logging_config["formatters"]["console"] = {
                "()": "app.common.logging_setup.ColoredFormatter",
                "format": "%(message)s",
            }

        if config.enable_file_logging:
            file_formatter: Literal["json", "detailed"] = (
                "json" if config.use_json_format else "detailed"
            )
            logging_config["handlers"]["file"] = {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": str(config.log_file),
                "maxBytes": config.max_file_size_mb * 1024 * 1024,
                "backupCount": config.backup_count,
                "formatter": file_formatter,
                "level": config.level,
                "encoding": "utf-8",
            }
            logging_config["root"]["handlers"].append("file")

        if config.enable_console_logging:
            logging_config["handlers"]["console"] = {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
                "formatter": "console",
                "level": config.console_level,
            }
            logging_config["root"]["handlers"].append("console")

        logging_config["loggers"]["app"] = {
            "level": "DEBUG",
            "propagate": True,
        }

        logging_config["loggers"]["urllib3"] = {
            "level": "WARNING",
            "propagate": True,
        }

        logging_config["loggers"]["requests"] = {
            "level": "WARNING",
            "propagate": True,
        }

        logging_config["loggers"]["openpyxl"] = {
            "level": "WARNING",
            "propagate": True,
        }

        logging_config["loggers"]["pd"] = {
            "level": "WARNING",
            "propagate": True,
        }

        return logging_config

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)


def get_logger(name: str) -> logging.Logger:

    return logging.getLogger(name)


class TemporaryLogLevel(object):
    def __init__(self, logger: logging.Logger, level: int):
        self.logger: logging.Logger = logger
        self.level: int = level
        self.original_level: int = logger.level

    def __enter__(self) -> logging.Logger:
        self.logger.setLevel(self.level)
        return self.logger

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.logger.setLevel(self.original_level)
