from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import Literal

# Third-party imports
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class FileIOConfig(BaseSettings):
    allowed_source_file_extensions: list[str] = Field(
        default=["xlsx", "xls"],
        description="Allowed file extensions for upload.",
    )

    model_config = {
        "env_prefix": "STORAGE_",
    }


class DatabaseConfig(BaseSettings):
    path: Path | None = Field(
        default=None,
        description="Path to the DuckDB database file; None means in-memory.",
    )

    max_memory: str = Field(
        default="2GB",
        description="Maximum memory to use.",
    )

    enable_logging: bool = Field(
        default=True,
        description="Enable query logging for debugging.",
    )

    model_config = {
        "env_prefix": "DATABASE_",
    }


class LoggingConfig(BaseSettings):
    # Log levels
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )

    # File logging
    enable_file_logging: bool = Field(
        default=True,
        description="Enable logging to file",
    )

    log_file: Path = Field(
        default=Path("logs") / "app.log",
        description="Path to log file",
    )

    @field_validator("log_file")
    @classmethod
    def ensure_log_directory(cls, log_file: Path) -> Path:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        return log_file

    # Formatting
    use_json_format: bool = Field(
        default=False,
        description="Use JSON format for structured logging",
    )

    include_traceback: bool = Field(
        default=True,
        description="Include full traceback in error logs",
    )

    model_config = {
        "env_prefix": "LOG_",
    }


class AppConfig(BaseSettings):
    file_io_config: FileIOConfig = Field(
        default_factory=FileIOConfig,
        description="Storage configuration",
    )

    database_config: DatabaseConfig = Field(
        default_factory=DatabaseConfig,
        description="Database configuration",
    )

    logging_config: LoggingConfig = Field(
        default_factory=LoggingConfig,
        description="Logging configuration",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }
