from __future__ import annotations
from datetime import date
from pathlib import Path
from typing import Any

# Imports tiers
import pandas as pd
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Alignment, Border, Font, Side
from openpyxl.utils import get_column_letter

# Imports de l'application locale
from app.core.domain.models.programme import Programme
from app.core.domain.models.report_context import ReportContext
from app.core.domain.models.report_specification import ReportSpecification
from app.core.domain.predefined_objects.programmes import (
    RURAL_HOUSING_PROGRAMMES,
    get_programmes_dataframe,
)
from app.core.domain.predefined_objects.dairas_et_communes import (
    get_dairas_communes_dataframe,
)
from app.core.infrastructure.data.data_repository import DataRepository
from app.core.infrastructure.file_io.file_io_service import FileIOService
from app.core.services.report_generation.base.report_generator import ReportGenerator


class SituationFinanciereGenerator(ReportGenerator):
    __slots__ = ("_current_row", "_target_programme")

    def __init__(
        self,
        file_io_service: FileIOService,
        data_repository: DataRepository,
        report_specification: ReportSpecification,
        report_context: ReportContext,
    ) -> None:
        super().__init__(
            file_io_service, data_repository, report_specification, report_context
        )
        self._current_row: int = 1
        self._target_programme: Programme | None = None

    def set_target_programme(self, programme_name: str) -> None:
        self._logger.debug(f"Setting target programme: {programme_name}")

        # Find programme in the list
        for programme in RURAL_HOUSING_PROGRAMMES:
            if programme.name == programme_name:
                self._target_programme = programme
                self._logger.info(
                    f"Target programme set: {programme.name} "
                    f"(aid_value: {programme.aid_value}, consistance: {programme.consistance})"
                )
                return

        # Programme not found
        available_programmes = [p.name for p in RURAL_HOUSING_PROGRAMMES]
        error_msg: str = (
            f"Programme '{programme_name}' not found. "
            f"Available programmes: {available_programmes}"
        )
        self._logger.error(error_msg)
        raise ValueError(error_msg)

    def _verify_target_programme(self) -> None:
        if self._target_programme is None:
            error_msg: str = (
                "No target programme set. Please call set_target_programme() "
                "before generating the report."
            )
            self._logger.error(error_msg)
            raise RuntimeError(error_msg)

        self._logger.debug(f"Target programme verified: {self._target_programme.name}")

    def generate(
        self,
        source_file_paths: dict[str, Path],
        output_directory_path: Path,
    ) -> Path:
        self._verify_target_programme()
        return super().generate(source_file_paths, output_directory_path)

    def _create_predefined_tables(self) -> None:
        self._logger.debug("Creating reference tables")

        # Create programmes table
        try:
            self._logger.debug(f"Creating reference table 'programmes'")
            df: pd.DataFrame = get_programmes_dataframe()
            self._data_repository.create_table_from_dataframe("programmes", df)
            rows, cols = df.shape
            self._logger.info(
                f"Reference table 'programmes' created: {rows} rows and {cols} columns"
            )
        except Exception as error:
            self._logger.exception(
                f"Failed to create reference table 'programmes': {error}"
            )
            raise

        # Create dairas_communes table
        try:
            self._logger.debug(f"Creating reference table 'dairas_communes'")
            df: pd.DataFrame = get_dairas_communes_dataframe()
            self._data_repository.create_table_from_dataframe("dairas_communes", df)
            rows, cols = df.shape
            self._logger.info(
                f"Reference table 'dairas_communes' created: {rows} rows and {cols} columns"
            )
        except Exception as error:
            self._logger.exception(
                f"Failed to create reference table 'dairas_communes': {error}"
            )
            raise

    def _format_query_with_context(self, query_template: str) -> str:
        self._logger.debug("Formatting query template with report context")
        assert self._target_programme is not None

        formatted_query: str = query_template

        formatted_query = (
            formatted_query.replace("{programme}", f"'{self._target_programme.name}'")
            .replace("{aid_value}", str(self._target_programme.aid_value))
            .replace("{year}", str(self._report_context.year))
            .replace("{month}", str(self._report_context.month.number))
        )

        self._logger.debug(
            f"Placeholders replaced with: month={self._report_context.month.number}, "
            f"year={self._report_context.year}, "
            f"programme={self._target_programme.name}, "
            f"aid_value={self._target_programme.aid_value}"
        )

        self._logger.debug("Query formatting completed")
        return formatted_query

    def _add_content(
        self, sheet: Worksheet, query_results: dict[str, pd.DataFrame]
    ) -> None:
        self._add_header(sheet)
        self._add_table_headers(sheet)
        self._add_data_rows(sheet, query_results)
        self._add_totals_row(sheet, query_results)

    def _add_header(self, sheet: Worksheet) -> None:
        self._logger.debug("Adding report header")

        sheet[f"A{self._current_row}"] = (
            f"Situation financière du programme '{self._target_programme}' par daira et par commune"
        )
        sheet.merge_cells(f"A{self._current_row}:T{self._current_row}")
        sheet[f"A{self._current_row}"].font = Font(name="Arial", size=9, bold=True)
        sheet[f"A{self._current_row}"].alignment = Alignment(
            horizontal="center", vertical="center"
        )

        self._current_row += 1

        sheet[f"A{self._current_row}"] = (
            f"Arrêté au {self._report_context.reporting_date}"
        )
        sheet.merge_cells(f"A{self._current_row}:T{self._current_row}")
        sheet[f"A{self._current_row}"].font = Font(name="Arial", size=9, bold=True)
        sheet[f"A{self._current_row}"].alignment = Alignment(
            horizontal="center", vertical="center"
        )

        self._current_row += 1

        sheet[f"A{self._current_row}"] = f"DL de {self._report_context.wilaya}"
        sheet[f"A{self._current_row}"].font = Font(name="Arial", size=9, bold=True)

        self._current_row += 1

    def _add_table_headers(self, sheet: Worksheet) -> None:
        self._logger.debug("Adding table headers")

        sheet[f"F{self._current_row}"] = "Engagement par la BNH"
        sheet.merge_cells(f"F{self._current_row}:G{self._current_row}")

        sheet[f"H{self._current_row}"] = (
            "Engagement par le MHUV (décision d'inscription)"
        )
        sheet.merge_cells(f"H{self._current_row}:I{self._current_row}")

        self._current_row += 1
        span_end: int = self._current_row + 3

        sheet[f"A{self._current_row}"] = (
            "Programme"  # Use self._target.program to populate data row (merge all cells)
        )
        sheet.merge_cells(f"A{self._current_row}:A{span_end}")

        sheet[f"B{self._current_row}"] = (
            "Daira"  # Use get_dairas_communes_dataframe() to populate data rows for this column
        )
        sheet.merge_cells(f"B{self._current_row}:B{span_end}")

        sheet[f"C{self._current_row}"] = (
            "Commune"  # Use get_dairas_communes_dataframe() to populate data rows for this column
        )
        sheet.merge_cells(f"C{self._current_row}:C{span_end}")

        sheet[f"D{self._current_row}"] = (
            "Aides notifiées (1)"  # Data rows should be empty for this column
        )
        sheet.merge_cells(f"D{self._current_row}:D{span_end}")

        sheet[f"E{self._current_row}"] = (
            "Montants notifiés"  # Data rows should be empty for this column
        )
        sheet.merge_cells(f"E{self._current_row}:E{span_end}")

        sheet[f"F{self._current_row}"] = (
            "Aides inscrites"  # Use query_results to populate data rows for this column
        )
        sheet.merge_cells(f"F{self._current_row}:F{span_end}")

        sheet[f"G{self._current_row}"] = (
            "Montants inscrits"  # Use query_results to populate data rows for this column
        )
        sheet.merge_cells(f"G{self._current_row}:G{span_end}")

        sheet[f"H{self._current_row}"] = (
            "Aides inscrites (2)"  # Data rows should be empty for this column
        )
        sheet.merge_cells(f"H{self._current_row}:H{span_end}")

        sheet[f"I{self._current_row}"] = (
            "Montants inscrits (3)"  # Data rows should be empty for this column
        )
        sheet.merge_cells(f"I{self._current_row}:I{span_end}")

        sheet[f"J{self._current_row}"] = "Consommations"
        sheet.merge_cells(f"J{self._current_row}:Q{self._current_row}")

        sheet[f"R{self._current_row}"] = "Cumul (6) = (4) + (5)"
        sheet.merge_cells(f"R{self._current_row}:R{span_end}")

        sheet[f"S{self._current_row}"] = (
            "Solde sur engagement (3) - (6)"  # Data rows should be empty for this column
        )
        sheet.merge_cells(f"S{self._current_row}:S{span_end}")

        sheet[f"T{self._current_row}"] = (
            "Reste à inscrire (1) - (2)"  # Data rows should be empty for this column
        )
        sheet.merge_cells(f"T{self._current_row}:T{span_end}")

        self._current_row += 1

        sheet[f"J{self._current_row}"] = (
            f"Cumuls au 31/12/{self._report_context.year - 1}"
        )
        sheet.merge_cells(f"J{self._current_row}:M{self._current_row}")

        end_day: int = (
            self._report_context.month.last_day(self._report_context.year)
            if not self._report_context.month.is_current
            else date.today().day
        )

        sheet[f"N{self._current_row}"] = (
            f"Du 1 janvier {self._report_context.year} au {end_day} {self._report_context.month}"
        )
        sheet.merge_cells(f"N{self._current_row}:Q{self._current_row}")

        self._current_row += 1

        sheet.merge_cells(f"J{self._current_row}:L{self._current_row}")
        sheet[f"J{self._current_row}"] = "Aides"

        sheet[f"M{self._current_row}"] = (
            "Montant (4)"  # Use query_results to populate data rows for this column
        )

        sheet.merge_cells(f"N{self._current_row}:P{self._current_row}")
        sheet[f"N{self._current_row}"] = "Aides"

        sheet[f"Q{self._current_row}"] = (
            "Montant (5)"  # Use query_results to populate data rows for this column
        )

        self._current_row += 1

        sheet[f"J{self._current_row}"] = (
            "T1"  # Use query_results to populate data rows for this column
        )
        sheet[f"K{self._current_row}"] = (
            "T2"  # Use query_results to populate data rows for this column
        )
        sheet[f"L{self._current_row}"] = (
            "T3"  # Use query_results to populate data rows for this column
        )

        sheet[f"N{self._current_row}"] = (
            "T1"  # Use query_results to populate data rows for this column
        )
        sheet[f"O{self._current_row}"] = (
            "T2"  # Use query_results to populate data rows for this column
        )
        sheet[f"P{self._current_row}"] = (
            "T3"  # Use query_results to populate data rows for this column
        )

        # Apply formatting to all header cells
        for row in range(self._current_row - 3, self._current_row):
            for col_num in range(1, 21):  # A to T
                col_letter: str = get_column_letter(col_num)
                cell: Any = sheet[f"{col_letter}{row}"]
                cell.font = Font(name="Arial", size=9, bold=True)
                cell.alignment = Alignment(
                    horizontal="center", vertical="center", wrap_text=True
                )
                cell.border = Border(
                    left=Side(style="thin"),
                    right=Side(style="thin"),
                    top=Side(style="thin"),
                    bottom=Side(style="thin"),
                )

        self._current_row += 1

    def _add_data_rows(
        self, sheet: Worksheet, query_results: dict[str, pd.DataFrame]
    ) -> None: ...

    def _add_totals_row(
        self, sheet: Worksheet, query_results: dict[str, pd.DataFrame]
    ) -> None: ...

    def _finalize_formatting(self, sheet: Worksheet) -> None:
        self._logger.debug("Applying final formatting")

        # Page setup
        sheet.page_setup.orientation = "landscape"
        sheet.page_setup.fitToWidth = 1
        sheet.page_setup.fitToHeight = 0

        self._logger.info("Final formatting completed successfully")
