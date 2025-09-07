from __future__ import annotations

# Standard library imports
from pathlib import Path
import re
from typing import Any, Protocol
from logging import Logger

# Third-party imports
import pandas
from openpyxl import Workbook

# Local application imports
from app.utils.exceptions import DataLoadError
from app.config import StorageConfig
from app.utils.logging_setup import get_logger


class StorageService(Protocol):
    def load_data_from_file(self, filename: str) -> pandas.DataFrame: ...
    def save_data_to_file(self, data: Any, output_filename: str) -> None: ...
    def find_filename_matching_pattern(self, pattern: str) -> str | None: ...


class FileStorageService(object):
    __slots__ = ("_config", "_logger")

    def __init__(self, storage_config: StorageConfig) -> None:
        self._logger: Logger = get_logger("app.services.file_storage")
        self._logger.debug("Initializing file storage service")

        self._config: StorageConfig = storage_config

        self._logger.debug(f"Creating uploads directory: {self._config.uploads_dir}")
        self._config.uploads_dir.mkdir(parents=True, exist_ok=True)

        self._logger.debug(f"Creating results directory: {self._config.results_dir}")
        self._config.results_dir.mkdir(parents=True, exist_ok=True)

        self._logger.info(
            f"File storage service initialized - uploads: {self._config.uploads_dir}, results: {self._config.results_dir}"
        )
        self._logger.debug(
            f"Configuration - Max file size: {self._config.max_input_file_size_mb}MB, Allowed extensions: {self._config.allowed_input_file_extensions}"
        )

    def load_data_from_file(self, filename: str) -> pandas.DataFrame:
        self._logger.info(f"Loading data from file: {filename}")
        file_path: Path = self._config.uploads_dir / filename
        self._logger.debug(f"Full file path: {file_path}")

        self._verify_file_exists(file_path)
        self._verify_input_extension(file_path)
        self._verify_file_size(file_path)

        try:
            self._logger.debug("Analyzing file to find table start row")
            skiprows: int = self._find_table_start_row(file_path)
            self._logger.debug(f"Table starts at row {skiprows}")

            self._logger.debug("Reading Excel file with pandas")
            dataframe = pandas.read_excel(  # type: ignore
                file_path, dtype_backend="numpy_nullable", skiprows=skiprows
            )

            self._logger.info(
                f"Successfully loaded {len(dataframe)} rows and {len(dataframe.columns)} columns from {filename}"
            )
            self._logger.debug(f"Column names: {list(dataframe.columns)}")

            return dataframe
        except Exception as error:
            self._logger.exception(f"Failed to load data from {filename}: {error}")
            raise DataLoadError(file_path, error) from error

    def save_data_to_file(self, data: Any, output_filename: str) -> None:
        self._logger.info(f"Saving data to file: {output_filename}")
        output_path: Path = self._config.results_dir / output_filename
        self._logger.debug(f"Full output path: {output_path}")

        self._verify_output_extension(output_filename)

        try:
            if isinstance(data, Workbook):
                self._logger.debug("Saving Excel workbook")
                data.save(output_path)
                self._logger.info(f"Successfully saved workbook to {output_filename}")
            else:
                self._logger.error(f"Unsupported data type for saving: {type(data)}")
                raise ValueError(f"Cannot save data of type {type(data)}")
        except Exception as error:
            self._logger.exception(f"Failed to save data to {output_filename}: {error}")
            raise

    def find_filename_matching_pattern(self, pattern: str) -> str | None:
        self._logger.debug(f"Searching for files matching pattern: {pattern}")

        try:
            regex: re.Pattern[str] = re.compile(pattern)
        except re.error as error:
            self._logger.exception(f"Invalid regex pattern '{pattern}': {error}")
            raise ValueError(f"Invalid regex pattern: {pattern}") from error

        self._logger.debug(f"Scanning directory: {self._config.uploads_dir}")
        matches: list[str] = [
            element.name
            for element in self._config.uploads_dir.iterdir()
            if element.is_file() and regex.match(element.name)
        ]

        self._logger.debug(f"Found {len(matches)} matching files: {matches}")

        if not matches:
            self._logger.warning(f"No files found matching pattern: {pattern}")
            return None

        if len(matches) > 1:
            error_msg = f"Multiple files matched pattern {pattern!r}: {matches}"
            self._logger.error(error_msg)
            raise ValueError(error_msg)

        matched_file = matches[0]
        self._logger.info(f"Found matching file: {matched_file}")
        return matched_file

    def _verify_file_exists(self, file_path: Path) -> None:
        self._logger.debug(f"Verifying file exists: {file_path}")
        if not file_path.exists():
            error_msg = f"File not found: {file_path}"
            self._logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        self._logger.debug("File exists")

    def _verify_input_extension(self, file_path: Path) -> None:
        extension: str = file_path.suffix.lstrip(".").lower()
        self._logger.debug(f"Verifying file extension: .{extension}")

        if extension not in self._config.allowed_input_file_extensions:
            error_msg = (
                f"Extension '.{extension}' not allowed. "
                f"Allowed: {self._config.allowed_input_file_extensions}"
            )
            self._logger.error(error_msg)
            raise ValueError(error_msg)
        self._logger.debug("File extension is valid")

    def _verify_file_size(self, file_path: Path) -> None:
        size_bytes = file_path.stat().st_size
        size_mb: float = size_bytes / (1024 * 1024)
        self._logger.debug(f"Verifying file size: {size_mb:.2f} MB")

        if size_mb > self._config.max_input_file_size_mb:
            error_msg = (
                f"File {file_path} is too large ({size_mb:.2f} MB). "
                f"Max allowed: {self._config.max_input_file_size_mb} MB"
            )
            self._logger.error(error_msg)
            raise ValueError(error_msg)
        self._logger.debug("File size is within limits")

    def _verify_output_extension(self, output_filename: str) -> None:
        extension: str = Path(output_filename).suffix.lstrip(".").lower()
        self._logger.debug(f"Verifying output extension: .{extension}")

        if extension != self._config.default_output_format:
            error_msg = (
                f"Output format '.{extension}' does not match default output format "
                f"'{self._config.default_output_format}'"
            )
            self._logger.error(error_msg)
            raise ValueError(error_msg)
        self._logger.debug("Output extension is valid")

    def _find_table_start_row(self, file_path: Path) -> int:
        self._logger.debug(
            "Searching for table start row by looking for 'N° d'ordre' header"
        )

        try:
            preview_df: pandas.DataFrame = pandas.read_excel(file_path, nrows=30, header=None)  # type: ignore
            self._logger.debug(f"Loaded {len(preview_df)} preview rows")
        except Exception as error:
            self._logger.exception(f"Failed to read file preview: {error}")
            raise DataLoadError(file_path, error) from error

        for row_idx, (_, row) in enumerate(preview_df.iterrows()):
            first_cell: str = (
                str(row.iloc[0]).strip() if pandas.notna(row.iloc[0]) else ""
            )
            self._logger.debug(
                f"Row {row_idx}: '{first_cell[:50]}{'...' if len(first_cell) > 50 else ''}'"
            )

            if "N° d'ordre" in first_cell:
                self._logger.info(f"Found table header 'N° d'ordre' at row {row_idx}")
                return row_idx

        error_msg = "Could not find 'N° d'ordre' header to determine table start"
        self._logger.error(error_msg)
        raise DataLoadError(file_path, Exception(error_msg))
