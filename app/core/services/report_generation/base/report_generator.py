from __future__ import annotations

# Standard library imports
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING
from logging import Logger

# Third-party imports
import pandas as pd
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

# Local application imports
from app.core.domain.models.report_context import ReportContext
from app.core.infrastructure.data.data_repository import DataRepository
from app.core.infrastructure.file_io.file_io_service import FileIOService
from app.core.utils.exceptions import QueryExecutionError
from app.core.utils.logging_setup import get_logger

if TYPE_CHECKING:
    from app.core.domain.registry.report_specification_registry import (
        ReportSpecification,
    )


class ReportGenerator(ABC):
    __slots__ = (
        "_file_io_service",
        "_data_repository",
        "_report_specification",
        "_report_context",
        "_workbook",
        "_logger",
    )

    def __init__(
        self,
        file_io_service: FileIOService,
        data_repository: DataRepository,
        report_specification: ReportSpecification,
        report_context: ReportContext,
    ) -> None:
        self._logger: Logger = get_logger(__name__)
        self._logger.debug(f"Initializing {self.__class__.__name__}")

        self._file_io_service: FileIOService = file_io_service
        self._data_repository: DataRepository = data_repository
        self._report_specification: ReportSpecification = report_specification
        self._report_context: ReportContext = report_context
        self._workbook: Workbook | None = None

        self._logger.info(
            f"Generator initialized for report: {report_specification.display_name}"
        )
        self._logger.debug(
            f"Report context: wilaya={report_context.wilaya.value}, date={report_context.reporting_date}"
        )

    def generate(
        self,
        source_file_paths: dict[str, Path],
        output_directory_path: Path,
    ) -> Path:
        self._logger.info("Starting report generation process")

        try:
            step: int = 1

            self._logger.debug(f"Generation step {step}: Loading data into database")
            self._load_data_into_db(source_file_paths)
            self._logger.info("Data successfully loaded into database")

            self._logger.debug(f"Generation step {step}: Creating reference tables")
            self._create_predefined_tables()
            self._logger.info("Program reference table created successfully")

            self._logger.debug(f"Generation step {step}: Executing queries")
            query_results: dict[str, pd.DataFrame] = self._execute_queries()
            self._logger.info(f"Successfully executed {len(query_results)} queries")

            self._logger.debug(f"Generation step {step}: Creating Excel workbook")
            self._workbook = Workbook()
            self._workbook.remove(self._workbook.active)  # type: ignore
            sheet: Worksheet = self._workbook.create_sheet(
                self._report_specification.display_name
            )
            self._logger.info(
                f"Workbook created with sheet: {self._report_specification.display_name}"
            )

            self._logger.debug(f"Generation step {step}: Adding report content")
            self._add_content(sheet, query_results)
            self._logger.debug("Content added successfully")

            self._logger.debug(f"Generation step {step}: Applying final formatting")
            self._finalize_formatting(sheet)
            self._logger.debug("Final formatting applied successfully")

            self._logger.debug(f"Generation step {step}: Saving report")
            output_file_path: Path = (
                output_directory_path / self._generate_output_filename()
            )
            self._save_report(output_file_path)
            self._logger.info("Report generation completed successfully")

            return output_file_path

        except Exception as error:
            self._logger.exception(f"Report generation failed: {error}")
            raise

    def _load_data_into_db(self, source_file_paths: dict[str, Path]) -> None:
        self._logger.debug("Loading files into database tables")

        for table_name, file_path in source_file_paths.items():
            self._logger.debug(f"Loading file '{file_path}' into table '{table_name}'")
            try:
                df: pd.DataFrame = self._file_io_service.load_data_from_file(file_path)

                original_columns: list[str] = list(df.columns)
                df.columns = [column.strip() for column in df.columns]
                cleaned_columns: list[str] = list(df.columns)

                if original_columns != cleaned_columns:
                    self._logger.debug(f"Column names cleaned for table '{table_name}'")

                self._data_repository.create_table_from_dataframe(table_name, df)
                self._logger.info(
                    f"Table '{table_name}' loaded successfully: {len(df)} rows"
                )

                print(self._data_repository.summarize(table_name))

            except Exception as error:
                self._logger.error(
                    f"Failed to load file '{file_path}' into table '{table_name}': {error}"
                )
                raise

    @abstractmethod
    def _create_predefined_tables(self) -> None: ...

    def _execute_queries(self) -> dict[str, pd.DataFrame]:
        self._logger.debug("Executing report queries")

        results: dict[str, pd.DataFrame] = {}
        query_count: int = len(self._report_specification.queries)
        self._logger.debug(f"Preparing to execute {query_count} queries")

        for query_name, query_template in self._report_specification.queries.items():
            self._logger.debug(f"Executing query '{query_name}'")
            try:
                formatted_query: str = self._format_query_with_context(query_template)
                self._logger.debug(
                    f"Query '{query_name}' formatted with report context"
                )

                result_df: pd.DataFrame = self._data_repository.execute(formatted_query)
                results[query_name] = result_df

                self._logger.info(
                    f"Query '{query_name}' returned {len(result_df)} rows"
                )

            except Exception as error:
                self._logger.exception(f"Query '{query_name}' failed: {error}")
                raise QueryExecutionError(
                    f"Required query '{query_name}' failed", error
                )

        self._logger.info(f"All {query_count} queries executed successfully")
        return results

    @abstractmethod
    def _format_query_with_context(self, query_template: str) -> str: ...

    @abstractmethod
    def _add_content(
        self, sheet: Worksheet, query_results: dict[str, pd.DataFrame]
    ) -> None: ...

    @abstractmethod
    def _finalize_formatting(self, sheet: Worksheet) -> None: ...

    def _generate_output_filename(self) -> str:
        from app.core.utils.date_formatting import DateFormatter

        output_filename: str = self._report_specification.output_filename
        self._logger.debug(f"Output filename template: {output_filename}")

        output_filename = output_filename.replace(
            "{wilaya}", self._report_context.wilaya.value
        )
        output_filename = output_filename.replace(
            "{date}",
            DateFormatter.to_french_filename_date(self._report_context.reporting_date),
        )

        if not output_filename.endswith(".xlsx"):
            output_filename += ".xlsx"

        self._logger.debug(f"Generated filename: {output_filename}")
        return output_filename

    def _save_report(self, output_file_path: Path) -> None:
        self._logger.debug(f"Saving report to: {output_file_path}")

        if not self._workbook:
            error_msg: str = "No workbook created"
            self._logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            self._file_io_service.save_data_to_file(
                data=self._workbook,
                output_file_path=output_file_path,
            )
            self._logger.info(f"Report saved successfully: {output_file_path}")
        except Exception as error:
            self._logger.exception(f"Failed to save report: {error}")
            raise
