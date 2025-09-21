from __future__ import annotations

# Imports tiers
import pandas as pd
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Alignment, Border, Font, Side
from openpyxl.utils import get_column_letter

# Imports de l'application locale
from app.core.domain.models.report_context import ReportContext
from app.core.domain.models.report_specification import ReportSpecification
from app.core.domain.predefined_objects.programmes import get_programmes_dataframe
from app.core.domain.predefined_objects.dairas_et_communes import (
    get_dairas_communes_dataframe,
)
from app.core.domain.predefined_objects.dairas_et_communes import (
    DAIRA_COMMUNE_MAPPING,
    DAIRAS_TIZI_OUZOU,
)
from app.core.infrastructure.data.data_repository import DataRepository
from app.core.infrastructure.file_io.file_io_service import FileIOService
from app.core.services.report_generation.base.report_generator import ReportGenerator


class SituationFinanciereGenerator(ReportGenerator):
    __slots__ = ("_current_row",)

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

    def _create_predefined_tables(self) -> None:
        self._logger.debug("Creating reference tables")
        try:
            self._logger.debug(f"Creating reference table 'programmes'")

            df: pd.DataFrame = get_programmes_dataframe()
            self._data_repository.create_table_from_dataframe("programmes", df)

            rows, cols = df.shape
            self._logger.info(
                f"Reference table 'programmes' created: {rows} rows and {cols} columns"
            )
            self._logger.debug(f"Columns for 'programmes': {list(df.columns)}")

        except Exception as error:
            self._logger.exception(
                f"Failed to create reference table 'programmes': {error}"
            )
            raise

        try:
            self._logger.debug(f"Creating reference table 'dairas_communes'")

            df: pd.DataFrame = get_dairas_communes_dataframe()
            self._data_repository.create_table_from_dataframe("dairas_communes", df)

            rows, cols = df.shape
            self._logger.info(
                f"Reference table 'dairas_communes' created: {rows} rows and {cols} columns"
            )
            self._logger.debug(f"Columns for 'dairas_communes': {list(df.columns)}")

        except Exception as error:
            self._logger.exception(
                f"Failed to create reference table 'dairas_communes': {error}"
            )
            raise

    def _format_query_with_context(self, query_template: str) -> str:
        self._logger.debug("Formatting query template with report context")

        formatted_query: str = query_template

        if self._report_context.month:
            month_number: int = self._report_context.month.number
            year: int = self._report_context.year

            formatted_query = formatted_query.replace(
                "{month_number:02d}", f"{month_number:02d}"
            )
            formatted_query = formatted_query.replace(
                "{month_number}", str(month_number)
            )
            formatted_query = formatted_query.replace("{year}", str(year))

            self._logger.debug(
                f"Placeholders replaced with: month_number={month_number:02d}, year={year}"
            )

        formatted_query = formatted_query.replace(
            "{year}", str(self._report_context.year)
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

        # Tableau number in column O
        sheet[f"O{self._current_row}"] = "TABLEAU    01"
        sheet[f"O{self._current_row}"].font = Font(
            name="Arial", size=10, bold=True, color="FF0000"
        )
        sheet[f"O{self._current_row}"].alignment = Alignment(horizontal="right")

        self._current_row += 1

        # Row 2: Main title
        sheet[f"A{self._current_row}"] = (
            "SITUATION   FINANCIERE   DES PROGRAMMES  DE  LOGEMENTS  AIDES  PAR  PROGRAMME, DAIRA ET PAR COMMUNE"
        )
        sheet.merge_cells(f"A{self._current_row}:P{self._current_row}")
        sheet[f"A{self._current_row}"].font = Font(name="Arial", size=10, bold=True)
        sheet[f"A{self._current_row}"].alignment = Alignment(
            horizontal="center", vertical="center"
        )

        self._current_row += 1

        # Row 3: Programme name
        sheet[f"A{self._current_row}"] = (
            "PROGRAMME  DE  LOGEMENTS  AIDES EN  MILIEU  RURAL"
        )
        sheet.merge_cells(f"A{self._current_row}:P{self._current_row}")
        sheet[f"A{self._current_row}"].font = Font(name="Arial", size=10, bold=True)
        sheet[f"A{self._current_row}"].alignment = Alignment(
            horizontal="center", vertical="center"
        )

        self._current_row += 1

        # Row 4: Date
        sheet[f"A{self._current_row}"] = f"ARRETEE   AU  20/03/2025"
        sheet.merge_cells(f"A{self._current_row}:P{self._current_row}")
        sheet[f"A{self._current_row}"].font = Font(name="Arial", size=10, bold=True)
        sheet[f"A{self._current_row}"].alignment = Alignment(
            horizontal="center", vertical="center"
        )

        self._current_row += 2

        # Row 6: DL DE TIZI OUZOU
        sheet[f"A{self._current_row}"] = "DL.DE TIZI OUZOU"
        sheet[f"A{self._current_row}"].font = Font(name="Arial", size=10, bold=True)
        self._current_row += 1

    def _add_table_headers(self, sheet: Worksheet) -> None:
        self._logger.debug("Adding table headers")

        start_row = self._current_row

        # Move to actual header rows
        start_row += 1

        # First header row (main categories)
        # Column A-B: DAIRA and COMMUNES (spanning 3 rows)
        sheet[f"A{start_row}"] = "DAIRA"
        sheet.merge_cells(f"A{start_row}:A{start_row + 2}")

        sheet[f"B{start_row}"] = "COMMUNES"
        sheet.merge_cells(f"B{start_row}:B{start_row + 2}")

        # Column C: Yellow column
        sheet[f"C{start_row}"] = "NBRE D'AIDES INSCRITES (1)"
        sheet.merge_cells(f"C{start_row}:C{start_row + 2}")

        # Columns D-E: Yellow columns
        sheet[f"D{start_row}"] = "MONTANTS INSCRITS"
        sheet.merge_cells(f"D{start_row}:D{start_row + 2}")

        sheet[f"E{start_row}"] = "NBRE D'AIDES INSCRITS"
        sheet.merge_cells(f"E{start_row}:E{start_row + 2}")

        # Columns F-G: Yellow columns
        sheet[f"F{start_row}"] = "MONTANTS INSCRITS"
        sheet.merge_cells(f"F{start_row}:F{start_row + 2}")

        sheet[f"G{start_row}"] = "NOMBRE D'AIDES INSCRITS (2)"
        sheet.merge_cells(f"G{start_row}:G{start_row + 2}")

        # Column H: Yellow
        sheet[f"H{start_row}"] = "MONTANTS INSCRITS (3)"
        sheet.merge_cells(f"H{start_row}:H{start_row + 2}")

        # Column I: CONSOMMATIONS header
        sheet[f"I{start_row}"] = "CONSOMMATIONS"
        sheet.merge_cells(f"I{start_row}:N{start_row}")

        # Column O: Yellow column
        sheet[f"O{start_row}"] = "CUMULLEE (9)=(4)+(5)"
        sheet.merge_cells(f"O{start_row}:O{start_row + 2}")

        # Column P: Yellow column
        sheet[f"P{start_row}"] = "SOLDE (10)=(3)-(9)"
        sheet.merge_cells(f"P{start_row}:P{start_row + 2}")

        # Second header row (sub-categories under CONSOMMATIONS)
        second_row = start_row + 1

        # CUMULES AU 31/12/2024
        sheet[f"I{second_row}"] = "CUMULES AU 31/12/2024"
        sheet.merge_cells(f"I{second_row}:K{second_row}")

        # DE JANVIER 2025 A MARS 2024
        sheet[f"L{second_row}"] = "DE  JANVIER 2025 A MARS 2024"
        sheet.merge_cells(f"L{second_row}:N{second_row}")

        # Third header row (detail columns)
        third_row = start_row + 2

        sheet[f"I{third_row}"] = "NOMBRE D'AIDES"
        sheet[f"J{third_row}"] = "T1"
        sheet[f"K{third_row}"] = "T2"
        sheet[f"L{third_row}"] = "T3"
        sheet[f"M{third_row}"] = "MONTANT (4)"
        sheet[f"L{third_row}"] = "NOMBRE D'AIDES"
        sheet[f"M{third_row}"] = "T1"
        sheet[f"N{third_row}"] = "T2"
        sheet[f"O{third_row}"] = "T3"
        sheet[f"P{third_row}"] = "MONTANT (5)"

        # Apply formatting to all header cells
        for row in range(start_row, start_row + 3):
            for col_num in range(1, 17):  # A to P
                col_letter = get_column_letter(col_num)
                cell = sheet[f"{col_letter}{row}"]
                cell.font = Font(name="Arial", size=8, bold=True)
                cell.alignment = Alignment(
                    horizontal="center", vertical="center", wrap_text=True
                )
                cell.border = Border(
                    left=Side(style="thin"),
                    right=Side(style="thin"),
                    top=Side(style="thin"),
                    bottom=Side(style="thin"),
                )

        self._current_row = start_row + 3

    def _add_data_rows(
        self, sheet: Worksheet, query_results: dict[str, pd.DataFrame]
    ) -> None:
        self._logger.debug("Adding data rows")

        # Get all dairas in order
        dairas_order = sorted(DAIRAS_TIZI_OUZOU)

        for daira in dairas_order:
            # Get communes for this daira
            communes = sorted(DAIRA_COMMUNE_MAPPING.get(daira, []))

            if not communes:
                continue

            daira_start_row = self._current_row

            # Add daira name (merge cells if multiple communes)
            sheet[f"A{daira_start_row}"] = daira
            if len(communes) > 1:
                sheet.merge_cells(
                    f"A{daira_start_row}:A{daira_start_row + len(communes) - 1}"
                )

            # Format daira cell
            for i in range(len(communes)):
                cell = sheet[f"A{daira_start_row + i}"]
                cell.font = Font(name="Arial", size=8)
                cell.alignment = Alignment(horizontal="left", vertical="center")
                cell.border = Border(
                    left=Side(style="thin"),
                    right=Side(style="thin"),
                    top=Side(style="thin"),
                    bottom=Side(style="thin"),
                )

            # Add data for each commune
            for idx, commune in enumerate(communes):
                row_num = daira_start_row + idx

                # Commune name
                sheet[f"B{row_num}"] = commune
                sheet[f"B{row_num}"].font = Font(name="Arial", size=8)

                # Yellow columns with sample data (these would be filled from queries)
                # Column C: Number with yellow background
                sheet[f"C{row_num}"] = 0

                # Column D: Amount with yellow background
                sheet[f"D{row_num}"] = 0

                # Column E: Number with yellow background
                sheet[f"E{row_num}"] = 0

                # Column F: Amount with yellow background
                sheet[f"F{row_num}"] = 0

                # Column G: Number with yellow background
                sheet[f"G{row_num}"] = 0

                # Column H: Amount with yellow background
                sheet[f"H{row_num}"] = 0

                # White columns (empty, no data)
                sheet[f"I{row_num}"] = 0  # Would be calculated
                sheet[f"J{row_num}"] = 0  # T1 yellow
                sheet[f"K{row_num}"] = 0  # T2 yellow
                sheet[f"L{row_num}"] = 0  # T3 yellow
                sheet[f"M{row_num}"] = 0  # Montant yellow
                sheet[f"L{row_num}"] = 0  # Would be from query
                sheet[f"M{row_num}"] = 0  # T1 yellow
                sheet[f"N{row_num}"] = 0  # T2 yellow
                sheet[f"O{row_num}"] = 0  # T3 yellow
                sheet[f"P{row_num}"] = 0  # Montant yellow

                # Column O: Cumulated (yellow)
                sheet[f"O{row_num}"] = 0

                # Column P: Balance (yellow)
                sheet[f"P{row_num}"] = 0

                # Apply formatting to all cells in the row
                for col_num in range(1, 17):  # A to P
                    col_letter = get_column_letter(col_num)
                    cell = sheet[f"{col_letter}{row_num}"]
                    if not cell.font:
                        cell.font = Font(name="Arial", size=8)
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.border = Border(
                        left=Side(style="thin"),
                        right=Side(style="thin"),
                        top=Side(style="thin"),
                        bottom=Side(style="thin"),
                    )

            self._current_row += len(communes)

    def _add_totals_row(
        self, sheet: Worksheet, query_results: dict[str, pd.DataFrame]
    ) -> None:
        self._logger.debug("Adding totals row")

        # Total row
        sheet[f"A{self._current_row}"] = "TOTAL"
        sheet.merge_cells(f"A{self._current_row}:B{self._current_row}")

        # Add calculated totals (would come from queries)
        # All yellow columns get totals
        sheet[f"C{self._current_row}"] = 0  # Total aides

        sheet[f"D{self._current_row}"] = 0  # Total montants

        sheet[f"E{self._current_row}"] = 0

        sheet[f"F{self._current_row}"] = 0

        sheet[f"G{self._current_row}"] = 0

        sheet[f"H{self._current_row}"] = 0

        # White columns
        sheet[f"I{self._current_row}"] = 0

        # Yellow columns in consommations section
        sheet[f"J{self._current_row}"] = 0  # T1
        sheet[f"K{self._current_row}"] = 0  # T2
        sheet[f"L{self._current_row}"] = 0  # T3
        sheet[f"M{self._current_row}"] = 0  # Montant
        sheet[f"L{self._current_row}"] = 0
        sheet[f"M{self._current_row}"] = 0  # T1
        sheet[f"N{self._current_row}"] = 0  # T2
        sheet[f"O{self._current_row}"] = 0  # T3
        sheet[f"P{self._current_row}"] = 0  # Montant

        # Yellow final columns
        sheet[f"O{self._current_row}"] = 0  # Cumulated
        sheet[f"P{self._current_row}"] = 0  # Solde

        # Apply formatting to total row
        for col_num in range(1, 17):  # A to P
            col_letter = get_column_letter(col_num)
            cell = sheet[f"{col_letter}{self._current_row}"]
            cell.font = Font(name="Arial", size=9, bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = Border(
                left=Side(style="thin"),
                right=Side(style="thin"),
                top=Side(style="thin"),
                bottom=Side(style="thin"),
            )

    def _finalize_formatting(self, sheet: Worksheet) -> None:
        self._logger.debug("Applying final formatting")

        # Set column widths
        column_widths = {
            "A": 12,  # DAIRA
            "B": 18,  # COMMUNES
            "C": 10,  # NBRE
            "D": 12,  # MONTANTS
            "E": 10,  # NBRE
            "F": 12,  # MONTANTS
            "G": 10,  # NOMBRE
            "H": 12,  # MONTANTS
            "I": 10,  # NOMBRE
            "J": 8,  # T1
            "K": 8,  # T2
            "L": 8,  # T3
            "M": 12,  # MONTANT
            "L": 10,  # NOMBRE
            "M": 8,  # T1
            "N": 8,  # T2
            "O": 8,  # T3
            "P": 12,  # MONTANT
            "O": 12,  # CUMULLEE
            "P": 12,  # SOLDE
        }

        for col, width in column_widths.items():
            sheet.column_dimensions[col].width = width

        # Page setup
        sheet.page_setup.orientation = "landscape"
        sheet.page_setup.fitToWidth = 1
        sheet.page_setup.fitToHeight = 0
        sheet.page_margins.left = 0.5
        sheet.page_margins.right = 0.5
        sheet.page_margins.top = 0.5
        sheet.page_margins.bottom = 0.5

        self._logger.info("Final formatting completed successfully")
