# Standard library imports
from pathlib import Path
from typing import Any, Dict, List, Optional
from logging import Logger
import json

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
            dataframe: pd.DataFrame = pd.read_excel(
                source_file_path, 
                skiprows=skiprows,
                engine='openpyxl'
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

                if output_file_path.exists():
                    try:
                        self._logger.debug(
                            "File already exists, trying to delete before saving"
                        )
                        output_file_path.unlink()
                    except PermissionError:
                        self._logger.error(
                            f"File {output_file_path} is open in another program (e.g., Excel). Please close it and retry."
                        )
                        raise

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
            # For pandas 1.5.3, use openpyxl engine explicitly
            preview_df: pd.DataFrame = pd.read_excel(
                source_file_path, 
                nrows=30, 
                header=None,
                engine='openpyxl'
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

    def load_additional_subprograms(self) -> List[Dict[str, Any]]:
        custom_file_path: Path = self._config.custom_subprograms_path

        if not custom_file_path.exists():
            self._logger.info(
                f"Additional subprograms file not found at '{custom_file_path}'. "
                "Creating template file for user customization."
            )
            self._create_custom_subprograms_file(custom_file_path)
            return []

        try:
            self._logger.debug(
                f"Reading additional subprograms file: {custom_file_path}"
            )

            with open(custom_file_path, "r", encoding="utf-8") as f:
                file_content: str = f.read().strip()

            if not file_content:
                self._logger.warning(
                    f"Additional subprograms file '{custom_file_path}' is empty. "
                    "No additional subprograms will be loaded."
                )
                return []

            self._logger.debug(f"Parsing JSON content from {custom_file_path}")
            data: Any = json.loads(file_content)

            if not isinstance(data, list):
                error_msg: str = (
                    f"Invalid format in '{custom_file_path}': expected JSON array, "
                    f"got {type(data).__name__}"
                )
                self._logger.error(error_msg)
                raise ValueError(error_msg)

            if not data:
                self._logger.info(
                    f"Additional subprograms file '{custom_file_path}' contains empty array. "
                    "No additional subprograms to load."
                )
                return []

            enabled_subprograms: List[Dict[str, Any]] = []
            disabled_count: int = 0

            for subprogram in data:
                if not isinstance(subprogram, dict):
                    self._logger.warning(
                        f"Skipping invalid subprogram entry (not a dict): {type(subprogram).__name__}"
                    )
                    continue

                is_enabled: bool = subprogram.get("enabled", True)
                subprogram_name: str = subprogram.get("name", "unnamed")

                if is_enabled:
                    enabled_subprograms.append(subprogram)
                    self._logger.debug(
                        f"Including enabled subprogram: '{subprogram_name}'"
                    )
                else:
                    disabled_count += 1
                    self._logger.debug(
                        f"Skipping disabled subprogram: '{subprogram_name}'"
                    )

            self._logger.info(
                f"Successfully loaded {len(enabled_subprograms)} enabled subprogram(s) "
                f"from '{custom_file_path}'"
            )

            if disabled_count > 0:
                self._logger.info(f"Skipped {disabled_count} disabled subprogram(s)")

            if enabled_subprograms:
                self._logger.debug(
                    f"Enabled subprogram names: {[item.get('name', 'unnamed') for item in enabled_subprograms]}"
                )

            return enabled_subprograms

        except json.JSONDecodeError as json_error:
            error_msg: str = (
                f"Invalid JSON format in '{custom_file_path}': {json_error}. "
                "Please verify the file contains valid JSON."
            )
            self._logger.error(error_msg)
            raise DataLoadError(custom_file_path, Exception(error_msg)) from json_error

        except Exception as error:
            error_msg: str = (
                f"Failed to load additional subprograms from '{custom_file_path}': {error}"
            )
            self._logger.error(error_msg)
            raise DataLoadError(custom_file_path, error) from error

    def _create_custom_subprograms_file(self, file_path: Path) -> None:
        try:
            self._logger.debug(
                f"Creating default custom subprograms file at: {file_path}"
            )

            template_content: List[Dict[str, Any]] = [
                {
                    "name": "Custom Subprogram",
                    "database_alias": "CUSTOM_PROGRAM_2025",
                    "enabled": False,
                    "notifications": [
                        {
                            "name": "N° 001",
                            "database_aliases": [
                                "N°:001.Du:01/01/2025.TRANCHE:0.Montant:   700 000",
                                "N° :001.Du:01/01/2025.TRANCHE:0.Montant:  700 000",
                            ],
                            "aid_count": 1009,
                            "aid_amount": 700000,
                        }
                    ],
                }
            ]

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(template_content, f, indent=2, ensure_ascii=False)

            self._logger.info(
                f"Created custom subprograms file with template data: {file_path}"
            )
            self._logger.info(
                "Note: Use 'enabled': true/false to control whether subprograms are loaded. "
                "Template example is disabled by default - set 'enabled': true to activate it."
            )

        except Exception as error:
            self._logger.error(
                f"Failed to create default custom subprograms file '{file_path}': {error}"
            )

    def ensure_custom_subprograms_file_exists(self) -> None:
        custom_file_path: Path = self._config.custom_subprograms_path
        if not custom_file_path.exists():
            self._create_custom_subprograms_file(custom_file_path)