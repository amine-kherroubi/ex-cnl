from __future__ import annotations

# Standard library imports
from abc import ABC, abstractmethod
from typing import Any

# Third-party imports
import pandas
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

# Local application imports
from app.data.data_repository import DataRepository
from app.services.document_generation.documents_registry import DocumentSpecification
from app.services.file_storage.file_storage_service import FileStorageService
from app.services.document_generation.context_management.document_context import (
    DocumentContext,
)
from app.utils.exceptions import QueryExecutionError


class DocumentGenerator(ABC):  # Template Method pattern
    __slots__ = (
        "_storage_service",
        "_data_repository",
        "_document_specification",
        "_document_context",
        "_workbook",
    )

    def __init__(
        self,
        storage_service: FileStorageService,
        data_repository: DataRepository,
        document_specification: DocumentSpecification,
        document_context: DocumentContext,
    ) -> None:
        self._storage_service: FileStorageService = storage_service
        self._data_repository: DataRepository = data_repository
        self._document_specification: DocumentSpecification = document_specification
        self._document_context: DocumentContext = document_context
        self._workbook: Workbook | None = None

    def generate(self) -> None:
        # Step 1: Validate required files
        files_matching_patterns: dict[str, str] = self._validate_required_files()

        # Step 2: Load data into in-memory database
        self._load_data_into_db(files_matching_patterns)

        # Step 3: Execute queries with parameter substitution  # CHANGE HERE: Updated comment
        query_results: dict[str, pandas.DataFrame] = self._execute_queries()

        # Step 4: Create workbook and main sheet
        self._workbook = Workbook()
        self._workbook.remove(self._workbook.active)  # type: ignore
        sheet: Worksheet = self._workbook.create_sheet(
            self._document_specification.display_name
        )

        # Step 5: Add header (subclass responsibility)
        self._add_header(sheet)

        # Step 6: Build main table (subclass responsibility)
        self._add_table(sheet, query_results)

        # Step 7: Add footer (subclass responsibility)
        self._add_footer(sheet)

        # Step 8: Final formatting (subclass responsibility)
        self._finalize_formatting(sheet)

        # Step 9: Save document
        self._save_document()

    def _validate_required_files(self) -> dict[str, str]:
        if not self._document_specification:
            raise ValueError("Document specification not set")

        missing_patterns: list[str] = []
        files_mapping: dict[str, str] = {}

        for pattern, view_name in self._document_specification.required_files.items():
            filename: str | None = self._storage_service.find_filename_matching_pattern(
                pattern
            )
            if filename is None:
                missing_patterns.append(pattern)
            else:
                files_mapping[view_name] = filename

        if missing_patterns:
            raise FileNotFoundError(
                f"Missing required files matching patterns: {missing_patterns}"
            )

        return files_mapping

    def _load_data_into_db(self, files_mapping: dict[str, str]) -> None:
        for view_name, filename in files_mapping.items():
            df: pandas.DataFrame = self._storage_service.load_data_from_file(filename)
            df.columns = [column.strip() for column in df.columns]
            self._data_repository.create_view_from_dataframe(view_name, df)

    def _execute_queries(self) -> dict[str, pandas.DataFrame]:
        if not self._document_specification:
            raise ValueError("Document specification not set")

        results: dict[str, pandas.DataFrame] = {}

        # CHANGE HERE: Added query parameter preparation and substitution
        # This allows dynamic SQL queries based on document context (dates, locations, etc.)
        query_params: dict[str, Any] = self._prepare_query_parameters()

        for query_name, query in self._document_specification.queries.items():
            try:
                # CHANGE HERE: Added parameter substitution using .format()
                # Queries can now contain placeholders like {month_start}, {wilaya}, etc.
                formatted_query: str = query.format(**query_params)
                results[query_name] = self._data_repository.execute(formatted_query)
            except Exception as error:
                raise QueryExecutionError(
                    f"Required query '{query_name}' failed", error
                )
        return results

    # CHANGE HERE: Completely new method added for preparing query parameters
    # This method extracts values from document context and formats them for SQL use
    def _prepare_query_parameters(self) -> dict[str, Any]:
        """Prepare parameters for SQL query substitution based on document context"""
        params: dict[str, Any] = {}

        # CHANGE HERE: Month and year parameter handling
        # Calculates month start/end dates, formats month names in different cases
        if self._document_context.month and self._document_context.year:
            # Calculate month start and end dates
            month_number: int = self._document_context.month.number
            last_day: int = self._document_context.month.last_day(
                self._document_context.year
            )

            params["month_start"] = (
                f"{self._document_context.year}-{month_number:02d}-01"
            )
            params["month_end"] = (
                f"{self._document_context.year}-{month_number:02d}-{last_day:02d}"
            )
            params["year"] = self._document_context.year
            params["month"] = self._document_context.month.value
            params["month_upper"] = self._document_context.month.value.upper()

        # CHANGE HERE: Wilaya (administrative division) parameter handling
        # Provides both normal and uppercase versions for flexible query usage
        if self._document_context.wilaya:
            params["wilaya"] = self._document_context.wilaya.value
            params["wilaya_upper"] = self._document_context.wilaya.value.upper()

        # CHANGE HERE: Semester parameter handling
        # Calculates semester date ranges (1st semester: Jan-Jun, 2nd semester: Jul-Dec)
        if self._document_context.semester:
            params["semester"] = self._document_context.semester
            # Calculate semester date ranges
            if self._document_context.semester == 1:
                params["semester_start"] = f"{self._document_context.year}-01-01"
                params["semester_end"] = f"{self._document_context.year}-06-30"
            else:
                params["semester_start"] = f"{self._document_context.year}-07-01"
                params["semester_end"] = f"{self._document_context.year}-12-31"

        # CHANGE HERE: Report date parameter handling
        # Formats specific report dates for SQL queries
        if self._document_context.report_date:
            params["report_date"] = self._document_context.report_date.strftime(
                "%Y-%m-%d"
            )

        return params

    @abstractmethod
    def _add_header(self, sheet: Worksheet) -> None: ...

    @abstractmethod
    def _add_table(
        self, sheet: Worksheet, query_results: dict[str, pandas.DataFrame]
    ) -> None: ...

    @abstractmethod
    def _add_footer(self, sheet: Worksheet) -> None: ...

    @abstractmethod
    def _finalize_formatting(self, sheet: Worksheet) -> None: ...

    def _save_document(self) -> None:
        if self._workbook:
            output_filename: str = self._document_specification.output_filename

            output_filename = output_filename.replace(
                "{wilaya}", self._document_context.wilaya.value
            )

            output_filename = output_filename.replace(
                "{date}", str(self._document_context.report_date)
            )

            if not output_filename.endswith(".xlsx"):
                output_filename += ".xlsx"

            self._storage_service.save_data_to_file(
                data=self._workbook,
                output_filename=output_filename,
            )
