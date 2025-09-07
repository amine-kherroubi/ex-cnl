from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import Literal

# Third-party imports
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class LoggingConfig(BaseSettings):
    # Log levels
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Global logging level",
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

    max_file_size_mb: int = Field(
        default=10,
        description="Maximum log file size in MB before rotation",
        gt=0,
        le=100,
    )

    backup_count: int = Field(
        default=5,
        description="Number of backup log files to keep",
        ge=0,
        le=20,
    )

    # Console logging
    enable_console_logging: bool = Field(
        default=True,
        description="Enable logging to console/CLI",
    )

    console_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Console-specific logging level",
    )

    # Formatting
    use_json_format: bool = Field(
        default=False,
        description="Use JSON format for structured logging",
    )

    include_traceback: bool = Field(
        default=True,
        description="Include full traceback in error logs",
    )

    # Performance
    disable_existing_loggers: bool = Field(
        default=False,
        description="Disable existing loggers when configuring",
    )

    @field_validator("log_file")
    @classmethod
    def ensure_log_directory(cls, log_file: Path) -> Path:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        return log_file

    model_config = {
        "env_prefix": "LOG_",
    }


class StorageConfig(BaseSettings):
    uploads_dir: Path = Field(
        default=Path("uploads"),
        description="Directory path where uploads are stored.",
    )

    results_dir: Path = Field(
        default=Path("results"),
        description="Directory path where results are stored.",
    )

    allowed_input_file_extensions: list[str] = Field(
        default=["xlsx", "xls"],
        description="Allowed file extensions for upload.",
    )

    max_input_file_size_mb: int = Field(
        default=50,
        description="Maximum allowed upload file size in megabytes.",
        gt=0,
        le=100,
    )

    default_output_format: Literal["xlsx", "xls"] = Field(
        default="xlsx",
        description="Default output format for results.",
    )

    @field_validator("uploads_dir")
    @classmethod
    def ensure_uploads_directory(cls, uploads_dir: Path) -> Path:
        uploads_dir.mkdir(parents=True, exist_ok=True)
        return uploads_dir

    @field_validator("results_dir")
    @classmethod
    def ensure_results_directory(cls, results_dir: Path) -> Path:
        results_dir.mkdir(parents=True, exist_ok=True)
        return results_dir

    model_config = {
        "env_prefix": "LOG_",
    }

    model_config = {
        "env_prefix": "STORAGE_",
    }


class DatabaseConfig(BaseSettings):
    path: Path | None = Field(
        default=None,
        description="Path to the DuckDB database file; None means in-memory.",
    )

    max_memory: str = Field(
        default="1GB",
        description="Maximum memory to use.",
    )

    enable_logging: bool = Field(
        default=True,
        description="Enable query logging for debugging.",
    )

    model_config = {
        "env_prefix": "DATABASE_",
    }


class AppConfig(BaseSettings):
    storage_config: StorageConfig = Field(
        default_factory=StorageConfig,
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
