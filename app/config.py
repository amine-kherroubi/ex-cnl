from __future__ import annotations

# Standard library imports
import os
import sys
import tempfile
import warnings
from pathlib import Path
from typing import Literal

# Third-party imports
from pydantic import BaseModel, Field, field_validator


def get_app_data_dir() -> Path:
    app_name: str = "GenerateurReports"

    if sys.platform == "win32":

        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if base:
            return Path(base) / app_name
        return Path.home() / "AppData" / "Local" / app_name

    elif sys.platform == "darwin":

        return Path.home() / "Library" / "Application Support" / app_name

    else:

        xdg_data = os.environ.get("XDG_DATA_HOME")
        if xdg_data:
            return Path(xdg_data) / app_name.lower()
        return Path.home() / ".local" / "share" / app_name.lower()


class FileIOConfig(BaseModel):
    allowed_source_file_extensions: list[str] = ["xlsx", "xls"]


class DatabaseConfig(BaseModel):
    path: Path | None = None
    max_memory: str = "1GB"
    enable_logging: bool = True


class LoggingConfig(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"
    enable_file_logging: bool = True
    enable_console_logging: bool = True
    log_file: Path = Field(
        default_factory=lambda: get_app_data_dir() / "logs" / "app.log"
    )
    use_json_format: bool = False
    include_traceback: bool = True
    console_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"
    max_file_size_mb: int = 10
    backup_count: int = 5
    disable_existing_loggers: bool = False

    @field_validator("log_file")
    @classmethod
    def ensure_log_directory(cls, log_file: Path) -> Path:

        try:

            log_file.parent.mkdir(parents=True, exist_ok=True)

            test_file = log_file.parent / ".write_test"
            test_file.write_text("test")
            test_file.unlink()

            return log_file

        except (OSError, PermissionError):

            temp_dir = Path(tempfile.gettempdir()) / "GenerateurReports"
            temp_log_file = temp_dir / "app.log"

            try:
                temp_dir.mkdir(parents=True, exist_ok=True)
                warnings.warn(
                    f"Cannot write to {log_file.parent}, using temporary location: {temp_log_file}",
                    UserWarning,
                )
                return temp_log_file
            except Exception:

                warnings.warn(
                    "Cannot create log file anywhere, file logging will be disabled",
                    UserWarning,
                )
                return Path("/dev/null")  # This will disable file logging


class AppConfig(BaseModel):
    file_io_config: FileIOConfig = Field(default_factory=FileIOConfig)
    database_config: DatabaseConfig = Field(default_factory=DatabaseConfig)
    logging_config: LoggingConfig = Field(default_factory=LoggingConfig)
