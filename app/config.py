from __future__ import annotations

# Standard library imports
import os
from pathlib import Path
from typing import Final
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StorageConfig:
    uploads_dir: Path
    results_dir: Path

    def __post_init__(self) -> None:
        for directory in [self.uploads_dir, self.results_dir]:
            directory.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True, slots=True)
class DatabaseConfig:
    connection_string: str | None = None
    memory_limit: str = "1GB"


@dataclass(frozen=True, slots=True)
class AppConfig:
    storage: StorageConfig
    database: DatabaseConfig
    max_file_size_mb: int = 100
    allowed_file_extensions: tuple[str, ...] = (".xlsx", ".xls", ".csv")
    default_output_format: str = "xlsx"


class ConfigManager:
    __slots__ = ()

    _instance: ConfigManager | None = None
    _config: AppConfig | None = None

    def __new__(cls) -> ConfigManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._config is None:
            self._config = self._load_config()

    @property
    def config(self) -> AppConfig:
        if self._config is None:
            self._config = self._load_config()
        return self._config

    def _load_config(self) -> AppConfig:
        base_dir: Path = Path(__file__).parent.parent.parent

        storage: StorageConfig = StorageConfig(
            uploads_dir=Path(os.getenv("UPLOADS_DIR", base_dir / "uploads")),
            results_dir=Path(os.getenv("RESULTS_DIR", base_dir / "results")),
        )

        database = DatabaseConfig(
            connection_string=os.getenv("DATABASE_CONNECTION"),
            memory_limit=os.getenv("DATABASE_MEMORY_LIMIT", "1GB"),
        )

        return AppConfig(
            storage=storage,
            database=database,
            max_file_size_mb=int(os.getenv("MAX_FILE_SIZE_MB", "100")),
        )

    def get_upload_path(self, filename: str) -> Path:
        return self.config.storage.uploads_dir / filename

    def get_result_path(self, filename: str) -> Path:
        return self.config.storage.results_dir / filename


DEFAULT_UPLOADS_DIR: Final[Path] = Path("uploads")
DEFAULT_RESULTS_DIR: Final[Path] = Path("results")
