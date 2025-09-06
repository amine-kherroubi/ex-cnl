from __future__ import annotations

# Standard library imports
from pathlib import Path
import re
from typing import Any, Protocol

# Third-party imports
import pandas
from openpyxl import Workbook

# Local application imports
from app.utils.exceptions import DataLoadError
from app.config import StorageConfig


class StorageService(Protocol):
    def load_data_from_file(self, filename: str) -> pandas.DataFrame: ...
    def save_data_to_file(self, data: Any, output_filename: str) -> None: ...
    def find_filename_matching_pattern(self, pattern: str) -> str | None: ...


class FileStorageService(object):
    __slots__ = ("_config",)

    def __init__(self, storage_config: StorageConfig) -> None:
        self._config: StorageConfig = storage_config
        self._config.uploads_dir.mkdir(parents=True, exist_ok=True)
        self._config.results_dir.mkdir(parents=True, exist_ok=True)

    def load_data_from_file(self, filename: str) -> pandas.DataFrame:
        file_path: Path = self._config.uploads_dir / filename

        self._verify_file_exists(file_path)
        self._verify_input_extension(file_path)
        self._verify_file_size(file_path)

        try:
            return pandas.read_excel(  # type: ignore
                file_path, dtype_backend="numpy_nullable"
            )
        except Exception as error:
            raise DataLoadError(file_path, error) from error

    def save_data_to_file(self, data: Any, output_filename: str) -> None:
        self._verify_output_extension(output_filename)

        if isinstance(data, Workbook):
            data.save(self._config.results_dir / output_filename)

    def find_filename_matching_pattern(self, pattern: str) -> str | None:
        regex: re.Pattern[str] = re.compile(pattern)

        matches: list[str] = [
            element.name
            for element in self._config.uploads_dir.iterdir()
            if element.is_file() and regex.match(element.name)
        ]

        if not matches:
            return None
        if len(matches) > 1:
            raise ValueError(f"Multiple files matched pattern {pattern!r}: {matches}")
        return matches[0]

    def _verify_file_exists(self, file_path: Path) -> None:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

    def _verify_input_extension(self, file_path: Path) -> None:
        extension: str = file_path.suffix.lstrip(".").lower()
        if extension not in self._config.allowed_input_file_extensions:
            raise ValueError(
                f"Extension '.{extension}' not allowed. "
                f"Allowed: {self._config.allowed_input_file_extensions}"
            )

    def _verify_file_size(self, file_path: Path) -> None:
        size_mb: float = file_path.stat().st_size / (1024 * 1024)
        if size_mb > self._config.max_input_file_size_mb:
            raise ValueError(
                f"File {file_path} is too large ({size_mb:.2f} MB). "
                f"Max allowed: {self._config.max_input_file_size_mb} MB"
            )

    def _verify_output_extension(self, output_filename: str) -> None:
        extension: str = Path(output_filename).suffix.lstrip(".").lower()
        if extension != self._config.default_output_format:
            raise ValueError(
                f"Output format '.{extension}' does not match default output format "
                f"'{self._config.default_output_format}'"
            )
