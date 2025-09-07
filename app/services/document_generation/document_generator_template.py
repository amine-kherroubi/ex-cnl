from __future__ import annotations

# Standard library imports
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable
from logging import Logger

# Third-party imports
import pandas
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

# Local application imports
from app.data.data_repository import DataRepository
from app.services.document_generation.business_values.programmes import (
    get_programmes_dataframe,
)
from app.services.file_storage.file_storage_service import FileStorageService
from app.services.document_generation.models.document_context import (
    DocumentContext,
)
from app.utils.exceptions import QueryExecutionError
from app.utils.date_formatting import DateFormatter
from app.utils.logging_setup import get_logger

if TYPE_CHECKING:
    from app.services.document_generation.document_registry import (
        DocumentSpecification,
    )


class DocumentGenerator(ABC):  # Template Method pattern
    __slots__ = (
        "_storage_service",
        "_data_repository",
        "_document_specification",
        "_document_context",
        "_workbook",
        "_logger",
    )

    def __init__(
        self,
        storage_service: FileStorageService,
        data_repository: DataRepository,
        document_specification: "DocumentSpecification",
        document_context: DocumentContext,
    ) -> None:
        self._logger: Logger = get_logger(f"app.generators.{self.__class__.__name__}")
        self._logger.debug(f"Initializing {self.__class__.__name__}")

        self._storage_service: FileStorageService = storage_service
        self._data_repository: DataRepository = data_repository
        self._document_specification: "DocumentSpecification" = document_specification
        self._document_context: DocumentContext = document_context
        self._workbook: Workbook | None = None

        self._logger.info(
            f"Generator initialized for document: {document_specification.display_name}"
        )
        self._logger.debug(
            f"Document context: wilaya={document_context.wilaya.value}, date={document_context.report_date}"
        )

    def generate(self) -> None:
        self._logger.info("Starting document generation process")

        try:
            # Step 1: Validate required files
            self._logger.debug("Step 1: Validating required files")
            files_matching_patterns: dict[str, str] = self._validate_required_files()
            self._logger.info(
                f"Found all required files: {list(files_matching_patterns.values())}"
            )

            # Step 2: Load data into in-memory database
            self._logger.debug("Step 2: Loading data into database")
            self._load_data_into_db(files_matching_patterns)
            self._logger.info("Data loaded successfully into database")

            # Step 3: Create programmes reference table
            self._logger.debug("Step 2.5: Creating programmes reference table")
            self._create_reference_tables()
            self._logger.info("Programmes reference table created successfully")

            # Step 4: Execute queries
            self._logger.debug("Step 3: Executing queries")
            query_results: dict[str, pandas.DataFrame] = self._execute_queries()
            self._logger.info(f"Executed {len(query_results)} queries successfully")

            # Step 5: Create workbook and main sheet
            self._logger.debug("Step 4: Creating Excel workbook")
            self._workbook = Workbook()
            self._workbook.remove(self._workbook.active)  # type: ignore
            sheet: Worksheet = self._workbook.create_sheet(
                self._document_specification.display_name
            )
            self._logger.info(
                f"Created workbook with sheet: {self._document_specification.display_name}"
            )

            # Step 6: Add header (subclass responsibility)
            self._logger.debug("Step 5: Adding document header")
            self._add_header(sheet)
            self._logger.debug("Header added successfully")

            # Step 7: Build main table (subclass responsibility)
            self._logger.debug("Step 6: Building main table")
            self._add_table(sheet, query_results)
            self._logger.debug("Main table built successfully")

            # Step 8: Add footer (subclass responsibility)
            self._logger.debug("Step 7: Adding document footer")
            self._add_footer(sheet)
            self._logger.debug("Footer added successfully")

            # Step 9: Final formatting (subclass responsibility)
            self._logger.debug("Step 8: Applying final formatting")
            self._finalize_formatting(sheet)
            self._logger.debug("Final formatting applied successfully")

            # Step 10: Save document
            self._logger.debug("Step 9: Saving document")
            self._save_document()
            self._logger.info("Document generation completed successfully")

        except Exception as error:
            self._logger.exception(f"Document generation failed: {error}")
            self._logger.exception("Full error details")
            raise

    def _validate_required_files(self) -> dict[str, str]:
        self._logger.debug("Validating required files")

        if not self._document_specification:
            error_msg: str = "Document specification not set"
            self._logger.error(error_msg)
            raise ValueError(error_msg)

        missing_patterns: list[str] = []
        files_mapping: dict[str, str] = {}

        self._logger.debug(
            f"Checking {len(self._document_specification.required_files)} required file patterns"
        )

        for pattern, view_name in self._document_specification.required_files.items():
            self._logger.debug(
                f"Looking for file matching pattern: {pattern} (view: {view_name})"
            )
            filename: str | None = self._storage_service.find_filename_matching_pattern(
                pattern
            )
            if filename is None:
                self._logger.warning(f"No file found for pattern: {pattern}")
                missing_patterns.append(pattern)
            else:
                self._logger.info(f"Found file '{filename}' for pattern: {pattern}")
                files_mapping[view_name] = filename

        if missing_patterns:
            error_msg: str = (
                f"Missing required files matching patterns: {missing_patterns}"
            )
            self._logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        self._logger.info(f"All {len(files_mapping)} required files found")
        return files_mapping

    def _load_data_into_db(self, files_mapping: dict[str, str]) -> None:
        self._logger.debug("Loading files into database views")

        for view_name, filename in files_mapping.items():
            self._logger.debug(f"Loading file '{filename}' into view '{view_name}'")
            try:
                df: pandas.DataFrame = self._storage_service.load_data_from_file(
                    filename
                )

                # Clean column names
                original_columns: list[str] = list(df.columns)
                df.columns = [column.strip() for column in df.columns]
                cleaned_columns: list[str] = list(df.columns)

                if original_columns != cleaned_columns:
                    self._logger.debug(f"Cleaned column names for view '{view_name}'")

                self._data_repository.create_view_from_dataframe(view_name, df)
                self._logger.info(
                    f"Successfully loaded view '{view_name}' with {len(df)} rows"
                )

                print(self._data_repository.summarize(view_name))

            except Exception as error:
                self._logger.error(
                    f"Failed to load file '{filename}' into view '{view_name}': {error}"
                )
                raise

    def _create_reference_tables(self) -> None:
        self._logger.debug("Creating reference tables")

        reference_tables: dict[str, Callable[[], pandas.DataFrame]] = {
            "programmes": get_programmes_dataframe,
        }

        for table_name, dataframe_factory in reference_tables.items():
            try:
                self._logger.debug(f"Creating '{table_name}' reference table")

                df: pandas.DataFrame = dataframe_factory()
                self._data_repository.create_view_from_dataframe(table_name, df)

                rows, cols = df.shape
                self._logger.info(
                    f"Created reference table '{table_name}' with {rows} rows and {cols} columns"
                )
                self._logger.debug(f"Columns for '{table_name}': {list(df.columns)}")

            except Exception as error:
                self._logger.exception(
                    f"Failed to create reference table '{table_name}': {error}"
                )
                raise

    def _execute_queries(self) -> dict[str, pandas.DataFrame]:
        self._logger.debug("Executing document queries")

        if not self._document_specification:
            error_msg = "Document specification not set"
            self._logger.error(error_msg)
            raise ValueError(error_msg)

        results: dict[str, pandas.DataFrame] = {}
        query_count: int = len(self._document_specification.queries)
        self._logger.debug(f"Preparing to execute {query_count} queries")

        for query_name, query_template in self._document_specification.queries.items():
            self._logger.debug(f"Executing query '{query_name}'")
            try:
                # Format query with document context
                formatted_query: str = self._format_query_with_context(query_template)
                self._logger.debug(
                    f"Formatted query '{query_name}' with document context"
                )

                result_df: pandas.DataFrame = self._data_repository.execute(
                    formatted_query
                )
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

    def _format_query_with_context(self, query_template: str) -> str:
        self._logger.debug("Formatting query template with document context")

        formatted_query: str = query_template

        if self._document_context.month:
            month_number: int = self._document_context.month.number
            year: int = self._document_context.year

            # Replace placeholders found in the query templates
            formatted_query = formatted_query.replace(
                "{month_number:02d}", f"{month_number:02d}"
            )
            formatted_query = formatted_query.replace(
                "{month_number}", str(month_number)
            )
            formatted_query = formatted_query.replace("{year}", str(year))

            self._logger.debug(
                f"Replaced placeholders with: month_number={month_number:02d}, year={year}"
            )

        # Also replace simple {year} for year-only queries
        formatted_query = formatted_query.replace(
            "{year}", str(self._document_context.year)
        )

        self._logger.debug("Query formatting completed")
        return formatted_query

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
        self._logger.debug("Preparing to save document")

        if not self._workbook:
            error_msg: str = "No workbook created"
            self._logger.error(error_msg)
            raise ValueError(error_msg)

        output_filename: str = self._document_specification.output_filename
        self._logger.debug(f"Output filename template: {output_filename}")

        # Use French date format for user-facing filenames
        output_filename = output_filename.replace(
            "{wilaya}", self._document_context.wilaya.value
        )
        output_filename = output_filename.replace(
            "{date}",
            DateFormatter.to_french_filename_date(self._document_context.report_date),
        )

        if not output_filename.endswith(".xlsx"):
            output_filename += ".xlsx"

        self._logger.info(f"Saving document as: {output_filename}")

        try:
            self._storage_service.save_data_to_file(
                data=self._workbook,
                output_filename=output_filename,
            )
            self._logger.info(f"Document saved successfully: {output_filename}")
        except Exception as error:
            self._logger.exception(f"Failed to save document: {error}")
            raise
