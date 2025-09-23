from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import Any
from logging import Logger

# Third-party imports
import pandas as pd
from openpyxl import Workbook

# Local application imports
from app.common.exceptions import DataLoadError
from app.config import FileIOConfig
from app.common.logging_setup import get_logger


class FileIOService(object):
    __slots__ = ("_config", "_logger")

    def __init__(self, file_io_config: FileIOConfig) -> None:
        self._logger: Logger = get_logger(__name__)
        self._logger.debug("Initializing file io service")

        self._config: FileIOConfig = file_io_config

        self._logger.info("File io service initialized")
        self._logger.debug(
            f"Allowed extensions: {self._config.allowed_source_file_extensions}"
        )

    def load_data_from_file(self, source_file_path: Path) -> pd.DataFrame:
        self._logger.info(f"Loading data from file: {source_file_path}")

        try:
            self._logger.debug("Analyzing file to find table start row")
            skiprows: int = self._find_table_start_row(source_file_path)
            self._logger.debug(f"Table starts at row {skiprows}")

            self._logger.debug("Reading Excel file with pandas")
            dataframe: pd.DataFrame = pd.read_excel(  # type: ignore
                source_file_path, dtype_backend="numpy_nullable", skiprows=skiprows
            )

            self._logger.info(
                f"Successfully loaded: {len(dataframe)} rows and {len(dataframe.columns)} columns from {source_file_path.name}"
            )
            self._logger.debug(f"Column names: {list(dataframe.columns)}")

            return dataframe

        except Exception as error:
            self._logger.exception(
                f"Failed to load data from {source_file_path}: {error}"
            )
            raise DataLoadError(source_file_path, error) from error

    def save_data_to_file(self, data: Any, output_file_path: Path) -> None:
        self._logger.info(f"Saving data to file: {output_file_path}")

        try:
            if isinstance(data, Workbook):
                self._logger.debug("Saving Excel workbook")
                output_file_path.parent.mkdir(parents=True, exist_ok=True)
                data.save(output_file_path)
                self._logger.info(f"Workbook saved successfully to {output_file_path}")
            else:
                self._logger.error(f"Unsupported data type for saving: {type(data)}")
                raise ValueError(f"Cannot save data of type {type(data)}")

        except Exception as error:
            self._logger.exception(f"Failed to save to {output_file_path}: {error}")
            raise

    def _find_table_start_row(self, source_file_path: Path) -> int:
        self._logger.debug(
            "Searching for table start row by looking for 'N° d'ordre' or 'Code décision' header"
        )

        try:
            preview_df: pd.DataFrame = pd.read_excel(  # type: ignore
                source_file_path, nrows=30, header=None
            )
            self._logger.debug(f"Loaded {len(preview_df)} preview rows")

        except Exception as error:
            self._logger.exception(f"Failed to read file preview: {error}")
            raise DataLoadError(source_file_path, error) from error

        for row_idx, (_, row) in enumerate(preview_df.iterrows()):
            first_cell: str = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            self._logger.debug(
                f"Row {row_idx}: '{first_cell[:50]}{'...' if len(first_cell) > 50 else ''}'"
            )

            if "N° d'ordre" in first_cell:
                self._logger.info(f"Table header 'N° d'ordre' found at row {row_idx}")
                return row_idx

            if "Code décision" in first_cell:
                self._logger.info(
                    f"Table header 'Code décision' found at row {row_idx}"
                )
                return row_idx

        error_msg: str = (
            "Unable to find 'N° d'ordre' or 'Code décision' header to determine table start"
        )
        self._logger.error(error_msg)
        raise DataLoadError(source_file_path, Exception(error_msg))
