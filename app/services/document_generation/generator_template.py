from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
import pandas
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from app.data.data_repository import DataRepository
from app.services.document_generation.documents_registry import DocumentDefinition
import re


class DocumentGenerator(ABC):  # Template Method pattern
    def __init__(self, repository: DataRepository) -> None:
        self._repository: DataRepository = repository
        self._document_definition: DocumentDefinition
        self._workbook: Workbook | None = None

    def generate(self, output_path: str) -> None:
        # Step 1: Validate required files
        self._validate_required_files()

        # Step 2: Execute queries
        query_results: dict[str, pandas.DataFrame] = self._execute_queries()

        # Step 3: Create workbook and main sheet
        self._workbook = Workbook()
        self._workbook.remove(self._workbook.active)  # type: ignore
        sheet: Any = self._workbook.create_sheet(self._document_definition.display_name)

        # Step 4: Add header (subclass responsibility)
        self._add_header(sheet)

        # Step 5: Build main table (subclass responsibility)
        self._add_table(sheet, query_results)

        # Step 6: Add footer (subclass responsibility)
        self._add_footer(sheet)

        # Step 7: Final formatting (subclass responsibility)
        self._finalize_formatting(sheet)

        # Step 8: Save document
        self._save_document(output_path)

    def _validate_required_files(self) -> None:
        if not self._document_definition:
            raise ValueError("Document definition not set")

        current_working_dir: Path = Path.cwd()
        available_files: list[str] = [
            p.name for p in current_working_dir.iterdir() if p.is_file()
        ]

        missing_patterns: list[str] = []
        for pattern in self._document_definition.required_files:
            regex: re.Pattern[str] = re.compile(pattern)
            if not any(regex.match(fname) for fname in available_files):
                missing_patterns.append(pattern)

        if missing_patterns:
            raise FileNotFoundError(
                f"Missing required files matching patterns: {missing_patterns}. "
                f"Available files: {available_files}"
            )

    def _execute_queries(self) -> dict[str, pandas.DataFrame]:
        if not self._document_definition:
            raise ValueError("Document definition not set")

        results: dict[str, pandas.DataFrame] = {}
        for query_name, query in self._document_definition.queries.items():
            try:
                results[query_name] = self._repository.execute_query(query)
            except Exception as e:
                print(f"Query '{query_name}' failed: {e}")
                results[query_name] = pandas.DataFrame()
        return results

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

    def _save_document(self, output_path: str) -> None:
        if self._workbook:
            self._workbook.save(output_path)
