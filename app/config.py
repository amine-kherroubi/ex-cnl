from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import Literal

# Third-party imports
from pydantic import Field
from pydantic_settings import BaseSettings


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

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


config: AppConfig = AppConfig()  # Ready-to-use instance
