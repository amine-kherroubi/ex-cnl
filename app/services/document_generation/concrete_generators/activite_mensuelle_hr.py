from __future__ import annotations

# Standard library imports
from typing import Any

# Third-party imports
import pandas
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

# Local application imports
from app.data.data_repository import DataRepository
from app.services.document_generation.document_generator_template import (
    DocumentGenerator,
)
from app.services.document_generation.models.document_context import DocumentContext
from app.services.document_generation.models.document_specification import (
    DocumentSpecification,
)
from app.services.file_storage.file_storage_service import FileStorageService


class ActiviteMensuelleHRGenerator(DocumentGenerator):
    __slots__ = ("_current_row",)

    def __init__(
        self,
        storage_service: FileStorageService,
        data_repository: DataRepository,
        document_specification: DocumentSpecification,
        document_context: DocumentContext,
    ) -> None:
        super().__init__(
            storage_service, data_repository, document_specification, document_context
        )
        self._current_row: int = 1

    def _add_header(self, sheet: Worksheet) -> None:
        self._logger.debug("Adding document header")

        # HABITAT RURAL - Set value first, then merge
        sheet[f"A{self._current_row}"] = "HABITAT RURAL"
        sheet.merge_cells(f"A{self._current_row}:E{self._current_row}")
        sheet[f"A{self._current_row}"].font = Font(name="Arial", size=9, bold=True)
        sheet[f"A{self._current_row}"].alignment = Alignment(
            horizontal="center", vertical="center"
        )
        self._logger.debug("Added main title: HABITAT RURAL")

        self._current_row += 1

        # Wilaya
        wilaya_text = f"WILAYA DE : {self._document_context.wilaya.value.upper()}"
        sheet[f"A{self._current_row}"] = wilaya_text
        sheet[f"A{self._current_row}"].font = Font(name="Arial", size=9, bold=True)
        self._logger.debug(f"Added wilaya: {wilaya_text}")

        # Main title - Set value first, then merge
        self._current_row += 1
        sheet[f"A{self._current_row}"] = (
            "ACTIVITE MENSUELLE PAR PROGRAMMES (À renseigner par la BNH (ex-CNL))"
        )
        sheet.merge_cells(f"A{self._current_row}:E{self._current_row}")
        sheet[f"A{self._current_row}"].font = Font(name="Arial", size=9, bold=True)
        sheet[f"A{self._current_row}"].alignment = Alignment(
            horizontal="center", vertical="center", wrap_text=True
        )
        self._logger.debug("Added document title")

        # Month - Set value first, then merge
        self._current_row += 1
        month_text: str = (
            f"MOIS DE {self._document_context.month.value.upper()} {self._document_context.year}"
        )
        sheet[f"A{self._current_row}"] = month_text
        sheet.merge_cells(f"A{self._current_row}:E{self._current_row}")
        sheet[f"A{self._current_row}"].font = Font(name="Arial", size=9, bold=True)
        sheet[f"A{self._current_row}"].alignment = Alignment(
            horizontal="center", vertical="center"
        )
        self._logger.debug(f"Added month and year: {month_text}")

        self._logger.info("Document header completed successfully")

        self._current_row += 2

    def _add_tables(
        self, sheet: Worksheet, query_results: dict[str, pandas.DataFrame]
    ) -> None:
        self._logger.debug("Adding main data table")
        self._logger.debug(f"Available query results: {list(query_results.keys())}")

        # Caption row (part of table) - Set value first, then merge
        caption_text: str = (
            f"ETAT D'EXECUTION DES TRANCHES FINANCIERES DURANT LE MOIS DE {self._document_context.month.value.upper()} {self._document_context.year}"
        )
        sheet[f"A{self._current_row}"] = caption_text
        sheet.merge_cells(f"A{self._current_row}:E{self._current_row}")
        sheet[f"A{self._current_row}"].font = Font(name="Arial", size=9, bold=True)
        sheet[f"A{self._current_row}"].alignment = Alignment(
            horizontal="center", vertical="center", wrap_text=True
        )
        self._logger.debug("Added table caption")

        # Headers
        self._current_row += 2
        headers: list[tuple[str, str]] = [
            ("A", "PROGRAMMES"),
            ("B", "LIVRAISONS (libération de la dernière TR)"),
            ("C", "CUMUL LIVRAISONS"),
            ("D", "LANCEMENTS (libération de la 1ère TR)"),
            ("E", "CUMUL LANCEMENTS"),
        ]

        self._logger.debug(
            f"Adding {len(headers)} column headers at row {self._current_row}"
        )
        for col, title in headers:
            cell = sheet[f"{col}{self._current_row}"]
            cell.value = title
            cell.font = Font(name="Arial", size=9, bold=True)
            cell.alignment = Alignment(
                horizontal="center", vertical="center", wrap_text=True
            )
            cell.fill = PatternFill(
                start_color="F2F2F2", end_color="F2F2F2", fill_type="solid"
            )
            cell.border = Border(
                left=Side(style="thin"),
                right=Side(style="thin"),
                top=Side(style="thin"),
                bottom=Side(style="thin"),
            )

        # Sub-headers
        self._current_row += 1
        month_short: str = self._document_context.month.value[:3].title()
        year_short: str = str(self._document_context.year)[-2:]

        sheet[f"B{self._current_row}"] = f"{month_short}-{year_short}"
        sheet[f"C{self._current_row}"] = (
            f"Cumul de JANVIER au 31 {self._document_context.month.value.upper()} {self._document_context.year}"
        )
        sheet[f"D{self._current_row}"] = f"{month_short}-{year_short}"
        sheet[f"E{self._current_row}"] = (
            f"Cumul de JANVIER au 31 {self._document_context.month.value.upper()} {self._document_context.year}"
        )

        for col in ["B", "C", "D", "E"]:
            cell = sheet[f"{col}{self._current_row}"]
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
        self._logger.debug("Added sub-headers with date ranges")

        # Add data from query results
        self._current_row += 1
        self._logger.debug(f"Starting data rows at row {self._current_row}")

        # Get all programmes with proper ordering
        programmes: list[str] = []
        if "programmes" in query_results:
            # Programmes are sorted by display_order
            programmes: list[str] = query_results["programmes"]["programme"].tolist()
            self._logger.info(
                f"Found {len(programmes)} programmes (pre-sorted by year): {programmes}"
            )
        else:
            self._logger.warning("No 'programmes' query result found")

        # Create lookup dictionaries for each metric
        self._logger.debug("Creating lookup dictionaries from query results")

        lancements_mois_dict: dict[str, int] = {}
        if "lancements_mois" in query_results:
            df_lm: pandas.DataFrame = query_results["lancements_mois"]
            lancements_mois_dict = dict(zip(df_lm["programme"], df_lm["count"]))
            self._logger.debug(
                f"Lancements month data: {len(lancements_mois_dict)} programmes"
            )
        else:
            self._logger.warning("No 'lancements_mois' query result found")

        lancements_cumul_annee_dict: dict[str, int] = {}
        if "lancements_cumul_annee" in query_results:
            df_ly: pandas.DataFrame = query_results["lancements_cumul_annee"]
            lancements_cumul_annee_dict = dict(zip(df_ly["programme"], df_ly["count"]))
            self._logger.debug(
                f"Lancements YTD data: {len(lancements_cumul_annee_dict)} programmes"
            )
        else:
            self._logger.warning("No 'lancements_cumul_annee' query result found")

        livraisons_mois_dict: dict[str, int] = {}
        if "livraisons_mois" in query_results:
            df_livm: pandas.DataFrame = query_results["livraisons_mois"]
            livraisons_mois_dict = dict(zip(df_livm["programme"], df_livm["count"]))
            self._logger.debug(
                f"Livraisons month data: {len(livraisons_mois_dict)} programmes"
            )
        else:
            self._logger.warning("No 'livraisons_mois' query result found")

        livraisons_cumul_annee_dict: dict[str, int] = {}
        if "livraisons_cumul_annee" in query_results:
            df_livy: pandas.DataFrame = query_results["livraisons_cumul_annee"]
            livraisons_cumul_annee_dict = dict(
                zip(df_livy["programme"], df_livy["count"])
            )
            self._logger.debug(
                f"Livraisons YTD data: {len(livraisons_cumul_annee_dict)} programmes"
            )
        else:
            self._logger.warning("No 'livraisons_cumul_annee' query result found")

        # Calculate totals
        total_livraisons_mois: int = sum(livraisons_mois_dict.values())
        total_livraisons_cumul_annee: int = sum(livraisons_cumul_annee_dict.values())
        total_lancements_mois: int = sum(lancements_mois_dict.values())
        total_lancements_cumul_annee: int = sum(lancements_cumul_annee_dict.values())

        self._logger.info(
            f"Calculated totals - Livraisons: {total_livraisons_mois} (month), {total_livraisons_cumul_annee} (YTD)"
        )
        self._logger.info(
            f"Calculated totals - Lancements: {total_lancements_mois} (month), {total_lancements_cumul_annee} (YTD)"
        )

        # Add data rows for each programme
        self._logger.debug(f"Adding data rows for {len(programmes)} programmes")
        for i, programme in enumerate(programmes):
            row: int = self._current_row + i
            self._logger.debug(f"Processing programme '{programme}' at row {row}")

            # Column A: Programme name
            sheet[f"A{row}"] = programme
            sheet[f"A{row}"].font = Font(name="Arial", size=9)

            # Column B: Livraisons (Month)
            livraisons_mois: int = livraisons_mois_dict.get(programme, 0)
            sheet[f"B{row}"] = livraisons_mois if livraisons_mois > 0 else "-"
            sheet[f"B{row}"].font = Font(name="Arial", size=9)

            # Column C: Livraisons (YTD)
            livraisons_cumul_annee: int = livraisons_cumul_annee_dict.get(programme, 0)
            sheet[f"C{row}"] = (
                livraisons_cumul_annee if livraisons_cumul_annee > 0 else "-"
            )
            sheet[f"C{row}"].font = Font(name="Arial", size=9)

            # Column D: Lancements (Month)
            lancements_mois: int = lancements_mois_dict.get(programme, 0)
            sheet[f"D{row}"] = lancements_mois if lancements_mois > 0 else "-"
            sheet[f"D{row}"].font = Font(name="Arial", size=9)

            # Column E: Lancements (YTD)
            lancements_cumul_annee: int = lancements_cumul_annee_dict.get(programme, 0)
            sheet[f"E{row}"] = (
                lancements_cumul_annee if lancements_cumul_annee > 0 else "-"
            )
            sheet[f"E{row}"].font = Font(name="Arial", size=9)

            # Add borders
            for col in ["A", "B", "C", "D", "E"]:
                cell = sheet[f"{col}{row}"]
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = Border(
                    left=Side(style="thin"),
                    right=Side(style="thin"),
                    top=Side(style="thin"),
                    bottom=Side(style="thin"),
                )

            if (
                livraisons_mois > 0
                or lancements_mois > 0
                or livraisons_cumul_annee > 0
                or lancements_cumul_annee > 0
            ):
                self._logger.debug(
                    f"Programme '{programme}': L={livraisons_mois}/{livraisons_cumul_annee}, La={lancements_mois}/{lancements_cumul_annee}"
                )

        # Add TOTAL row
        self._current_row += len(programmes)
        self._logger.debug(f"Adding TOTAL row at row {self._current_row}")

        sheet[f"A{self._current_row}"] = "TOTAL"
        sheet[f"B{self._current_row}"] = total_livraisons_mois
        sheet[f"C{self._current_row}"] = total_livraisons_cumul_annee
        sheet[f"D{self._current_row}"] = total_lancements_mois
        sheet[f"E{self._current_row}"] = total_lancements_cumul_annee

        # Format TOTAL row
        for col in ["A", "B", "C", "D", "E"]:
            cell: Any = sheet[f"{col}{self._current_row}"]
            cell.font = Font(name="Arial", size=9, bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.fill = PatternFill(
                start_color="E7E6E6", end_color="E7E6E6", fill_type="solid"
            )
            cell.border = Border(
                left=Side(style="thin"),
                right=Side(style="thin"),
                top=Side(style="thin"),
                bottom=Side(style="thin"),
            )

        self._logger.info(
            f"Main table completed with {len(programmes)} programmes plus totals"
        )

        self._current_row += 2

        self._add_second_table_header(sheet)

    def _add_second_table_header(self, sheet: Worksheet) -> None:
        sheet[f"A{self._current_row}"] = (
            "SITUATION DES PROGRAMMES (À renseigner par la BNH (ex-CNL))"
        )
        sheet.merge_cells(f"A{self._current_row}:E{self._current_row}")
        sheet[f"A{self._current_row}"].font = Font(name="Arial", size=9, bold=True)
        sheet[f"A{self._current_row}"].alignment = Alignment(
            horizontal="center", vertical="center"
        )

        self._current_row += 1
        sheet[f"A{self._current_row}"] = "ARRÊTÉE AU : 20/12/2024"
        sheet.merge_cells(f"A{self._current_row}:E{self._current_row}")
        sheet[f"A{self._current_row}"].font = Font(name="Arial", size=9, bold=True)
        sheet[f"A{self._current_row}"].alignment = Alignment(
            horizontal="center", vertical="center"
        )

        self._current_row += 2

    def _add_footer(self, sheet: Worksheet) -> None:
        self._logger.debug("Adding document footer")

        # Left footer text (A-B)
        sheet.merge_cells(f"A{self._current_row}:B{self._current_row}")
        sheet[f"A{self._current_row}"] = "VISA DU DIRECTEUR REGIONAL BNH (ex-CNL)"
        sheet[f"A{self._current_row}"].font = Font(name="Arial", size=9, bold=True)
        sheet[f"A{self._current_row}"].alignment = Alignment(
            horizontal="left", vertical="center"
        )

        # Right footer text (D-E)
        sheet.merge_cells(f"D{self._current_row}:E{self._current_row}")
        sheet[f"D{self._current_row}"] = "VISA DU DIRECTEUR DU LOGEMENT"
        sheet[f"D{self._current_row}"].font = Font(name="Arial", size=9, bold=True)
        sheet[f"D{self._current_row}"].alignment = Alignment(
            horizontal="right", vertical="center"
        )

        self._logger.debug("Footer added successfully")

    def _finalize_formatting(self, sheet: Worksheet) -> None:
        self._logger.debug("Applying final formatting")

        column_widths: dict[str, int] = {"A": 25, "B": 18, "C": 22, "D": 18, "E": 22}
        self._logger.debug(f"Setting column widths: {column_widths}")

        for col, width in column_widths.items():
            sheet.column_dimensions[col].width = width

        sheet.page_setup.orientation = "portrait"
        sheet.page_setup.fitToWidth = 1
        sheet.page_setup.fitToHeight = 0

        self._logger.debug("Set page orientation to portrait with fit to width")
        self._logger.info("Final formatting completed successfully")
