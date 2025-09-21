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
    __slots__ = ("_current_row", "_target_programme", "_totals")

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
        """Set the target programme for the financial situation report."""
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
        available_programmes: list[str] = [p.name for p in RURAL_HOUSING_PROGRAMMES]
        error_msg: str = (
            f"Programme '{programme_name}' not found. "
            f"Available programmes: {available_programmes}"
        )
        self._logger.error(error_msg)
        raise ValueError(error_msg)

    def _verify_target_programme(self) -> None:
        """Verify that a target programme has been set."""
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
        """Generate the financial situation report."""
        self._verify_target_programme()
        return super().generate(source_file_paths, output_directory_path)

    def _create_predefined_tables(self) -> None:
        """Create reference tables needed for the report."""
        self._logger.debug("Creating reference tables")

        # Create programmes table
        try:
            self._logger.debug("Creating reference table 'programmes'")
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
            self._logger.debug("Creating reference table 'dairas_communes'")
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
        """Format query template with current report context and target programme."""
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
        """Add all content to the worksheet."""
        self._add_header(sheet)
        self._add_table_headers(sheet)
        self._add_data_rows(sheet, query_results)
        self._add_totals_row(sheet, query_results)

    def _add_header(self, sheet: Worksheet) -> None:
        """Add the report header section."""
        self._logger.debug("Adding report header")

        # Main title
        sheet[f"A{self._current_row}"] = (
            f"Situation financière du programme '{self._target_programme.name}' par daira et par commune"  # type: ignore
        )
        sheet.merge_cells(f"A{self._current_row}:T{self._current_row}")
        sheet[f"A{self._current_row}"].font = Font(name="Arial", size=12, bold=True)
        sheet[f"A{self._current_row}"].alignment = Alignment(
            horizontal="center", vertical="center"
        )

        self._current_row += 1

        # Report date
        sheet[f"A{self._current_row}"] = (
            f"Arrêté au {self._report_context.reporting_date.strftime('%d/%m/%Y')}"
        )
        sheet.merge_cells(f"A{self._current_row}:T{self._current_row}")
        sheet[f"A{self._current_row}"].font = Font(name="Arial", size=10, bold=True)
        sheet[f"A{self._current_row}"].alignment = Alignment(
            horizontal="center", vertical="center"
        )

        self._current_row += 1

        # Wilaya
        sheet[f"A{self._current_row}"] = f"DL de {self._report_context.wilaya.value}"
        sheet[f"A{self._current_row}"].font = Font(name="Arial", size=10, bold=True)

        self._current_row += 2

        self._logger.info("Report header added successfully")

    def _add_table_headers(self, sheet: Worksheet) -> None:
        """Add the complex table headers with merged cells."""
        self._logger.debug("Adding table headers")

        # First level headers (engagement types)
        sheet[f"F{self._current_row}"] = "Engagement par la BNH"
        sheet.merge_cells(f"F{self._current_row}:G{self._current_row}")

        sheet[f"H{self._current_row}"] = (
            "Engagement par le MHUV (décision d'inscription)"
        )
        sheet.merge_cells(f"H{self._current_row}:I{self._current_row}")

        self._current_row += 1
        header_start_row: int = self._current_row
        header_end_row: int = self._current_row + 3

        # Main column headers with vertical spans
        main_headers: list[tuple[str, str]] = [
            ("A", "Programme"),
            ("B", "Daira"),
            ("C", "Commune"),
            ("D", "Aides notifiées (1)"),
            ("E", "Montants notifiés"),
            ("F", "Aides inscrites"),
            ("G", "Montants inscrits"),
            ("H", "Aides inscrites (2)"),
            ("I", "Montants inscrits (3)"),
            ("R", "Cumul (6) = (4) + (5)"),
            ("S", "Solde sur engagement (3) - (6)"),
            ("T", "Reste à inscrire (1) - (2)"),
        ]

        for col, title in main_headers:
            sheet[f"{col}{self._current_row}"] = title
            sheet.merge_cells(f"{col}{header_start_row}:{col}{header_end_row}")

        # Consommations header
        sheet[f"J{self._current_row}"] = "Consommations"
        sheet.merge_cells(f"J{self._current_row}:Q{self._current_row}")

        self._current_row += 1

        # Second level headers (time periods)
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
            f"Du 1 janvier {self._report_context.year} au {end_day} {self._report_context.month.value}"
        )
        sheet.merge_cells(f"N{self._current_row}:Q{self._current_row}")

        self._current_row += 1

        # Third level headers (aid categories)
        sheet[f"J{self._current_row}"] = "Aides"
        sheet.merge_cells(f"J{self._current_row}:L{self._current_row}")
        sheet[f"M{self._current_row}"] = "Montant (4)"

        sheet[f"N{self._current_row}"] = "Aides"
        sheet.merge_cells(f"N{self._current_row}:P{self._current_row}")
        sheet[f"Q{self._current_row}"] = "Montant (5)"

        self._current_row += 1

        # Fourth level headers (tranche types)
        tranche_headers: list[tuple[str, str]] = [
            ("J", "T1"),
            ("K", "T2"),
            ("L", "T3"),
            ("N", "T1"),
            ("O", "T2"),
            ("P", "T3"),
        ]

        for col, title in tranche_headers:
            sheet[f"{col}{self._current_row}"] = title

        # Apply formatting to all header cells
        for row in range(header_start_row, self._current_row + 1):
            for col_num in range(1, 21):  # A to T (columns 1-20)
                col_letter: str = get_column_letter(col_num)
                cell: Any = sheet[f"{col_letter}{row}"]
                if cell.value:  # Only format cells that have content
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
        self._logger.info("Table headers added successfully")

    def _add_data_rows(
        self, sheet: Worksheet, query_results: dict[str, pd.DataFrame]
    ) -> None:
        """Add data rows to the table."""
        self._logger.debug("Adding data rows")

        # Get dairas and communes data
        dairas_communes_df: pd.DataFrame = get_dairas_communes_dataframe()

        # Create lookup dictionaries from query results
        aides_inscrites_dict: dict[tuple[str, str], tuple[int, int]] = {}
        if "nb_aides_et_montants_inscrits_par_daira_et_commune" in query_results:
            df_inscrites: pd.DataFrame = query_results[
                "nb_aides_et_montants_inscrits_par_daira_et_commune"
            ]
            for _, row in df_inscrites.iterrows():
                key: tuple[str, str] = (
                    row["Daira du projet"],
                    row["Commune du projet"],
                )
                aides_inscrites_dict[key] = (
                    row["nb_aides_inscrites"],
                    row["montant_inscrits"],
                )
            self._logger.debug(
                f"Loaded {len(aides_inscrites_dict)} inscribed aids records"
            )

        cumul_precedent_dict: dict[tuple[str, str], tuple[int, int, int, int]] = {}
        if "consommations_cumulees_fin_annee_precedente" in query_results:
            df_cumul: pd.DataFrame = query_results[
                "consommations_cumulees_fin_annee_precedente"
            ]
            for _, row in df_cumul.iterrows():
                key: tuple[str, str] = (row["Daira"], row["Commune de projet"])
                cumul_precedent_dict[key] = (
                    row["t_1"],
                    row["t_2"],
                    row["t_3"],
                    row["montant"],
                )
            self._logger.debug(
                f"Loaded {len(cumul_precedent_dict)} previous year cumulative records"
            )

        annee_actuelle_dict: dict[tuple[str, str], tuple[int, int, int, int]] = {}
        if "consommations_annee_actuelle_jusqua_mois_actuel" in query_results:
            df_actuelle: pd.DataFrame = query_results[
                "consommations_annee_actuelle_jusqua_mois_actuel"
            ]
            for _, row in df_actuelle.iterrows():
                key: tuple[str, str] = (row["Daira"], row["Commune de projet"])
                annee_actuelle_dict[key] = (
                    row["t_1"],
                    row["t_2"],
                    row["t_3"],
                    row["montant"],
                )
            self._logger.debug(
                f"Loaded {len(annee_actuelle_dict)} current year records"
            )

        # Track totals
        totals: dict[str, int] = {
            "aides_inscrites": 0,
            "montants_inscrits": 0,
            "cumul_precedent_t1": 0,
            "cumul_precedent_t2": 0,
            "cumul_precedent_t3": 0,
            "cumul_precedent_montant": 0,
            "annee_actuelle_t1": 0,
            "annee_actuelle_t2": 0,
            "annee_actuelle_t3": 0,
            "annee_actuelle_montant": 0,
            "cumul_total": 0,
        }

        # Add data rows for each daira/commune combination
        for i, (_, row) in enumerate(dairas_communes_df.iterrows()):
            daira: str = row["Daira"]
            commune: str = row["Commune"]
            current_row: int = self._current_row + i

            self._logger.debug(f"Processing row {current_row}: {daira} - {commune}")

            # Column A: Programme (use target programme name)
            sheet[f"A{current_row}"] = self._target_programme.name  # type: ignore

            # Column B: Daira
            sheet[f"B{current_row}"] = daira

            # Column C: Commune
            sheet[f"C{current_row}"] = commune

            # Column D: Aides notifiées (empty as indicated in comments)
            sheet[f"D{current_row}"] = "-"

            # Column E: Montants notifiés (empty as indicated in comments)
            sheet[f"E{current_row}"] = "-"

            # Columns F & G: Aides inscrites and Montants inscrits from query results
            key: tuple[str, str] = (daira, commune)

            # Initialize previous year values to ensure they're always defined
            t1_prev = t2_prev = t3_prev = montant_prev = 0

            if key in aides_inscrites_dict:
                aides_inscrites, montants_inscrits = aides_inscrites_dict[key]
                sheet[f"F{current_row}"] = (
                    aides_inscrites if aides_inscrites > 0 else "-"
                )
                sheet[f"G{current_row}"] = (
                    montants_inscrits if montants_inscrits > 0 else "-"
                )
                totals["aides_inscrites"] += aides_inscrites
                totals["montants_inscrits"] += montants_inscrits
            else:
                sheet[f"F{current_row}"] = "-"
                sheet[f"G{current_row}"] = "-"

            # Column H: Aides inscrites (2) (empty as indicated in comments)
            sheet[f"H{current_row}"] = "-"

            # Column I: Montants inscrits (3) (empty as indicated in comments)
            sheet[f"I{current_row}"] = "-"

            # Columns J, K, L, M: Cumuls au 31/12/previous_year from query results
            if key in cumul_precedent_dict:
                t1_prev, t2_prev, t3_prev, montant_prev = cumul_precedent_dict[key]
                sheet[f"J{current_row}"] = t1_prev if t1_prev > 0 else "-"
                sheet[f"K{current_row}"] = t2_prev if t2_prev > 0 else "-"
                sheet[f"L{current_row}"] = t3_prev if t3_prev > 0 else "-"
                sheet[f"M{current_row}"] = montant_prev if montant_prev > 0 else "-"
                totals["cumul_precedent_t1"] += t1_prev
                totals["cumul_precedent_t2"] += t2_prev
                totals["cumul_precedent_t3"] += t3_prev
                totals["cumul_precedent_montant"] += montant_prev
            else:
                sheet[f"J{current_row}"] = "-"
                sheet[f"K{current_row}"] = "-"
                sheet[f"L{current_row}"] = "-"
                sheet[f"M{current_row}"] = "-"

            # Columns N, O, P, Q: Current year from query results
            if key in annee_actuelle_dict:
                t1_curr, t2_curr, t3_curr, montant_curr = annee_actuelle_dict[key]
                sheet[f"N{current_row}"] = t1_curr if t1_curr > 0 else "-"
                sheet[f"O{current_row}"] = t2_curr if t2_curr > 0 else "-"
                sheet[f"P{current_row}"] = t3_curr if t3_curr > 0 else "-"
                sheet[f"Q{current_row}"] = montant_curr if montant_curr > 0 else "-"
                totals["annee_actuelle_t1"] += t1_curr
                totals["annee_actuelle_t2"] += t2_curr
                totals["annee_actuelle_t3"] += t3_curr
                totals["annee_actuelle_montant"] += montant_curr

                # Column R: Cumul (6) = (4) + (5)
                cumul_total: int = (
                    montant_prev + montant_curr
                    if key in cumul_precedent_dict
                    else montant_curr
                )
                sheet[f"R{current_row}"] = cumul_total if cumul_total > 0 else "-"
                totals["cumul_total"] += cumul_total
            else:
                sheet[f"N{current_row}"] = "-"
                sheet[f"O{current_row}"] = "-"
                sheet[f"P{current_row}"] = "-"
                sheet[f"Q{current_row}"] = "-"
                # Column R: Only previous year if no current year data
                if key in cumul_precedent_dict:
                    sheet[f"R{current_row}"] = (
                        cumul_precedent_dict[key][3]
                        if cumul_precedent_dict[key][3] > 0
                        else "-"
                    )
                    totals["cumul_total"] += cumul_precedent_dict[key][3]
                else:
                    sheet[f"R{current_row}"] = "-"

            # Column S: Solde sur engagement (3) - (6) (empty as indicated in comments)
            sheet[f"S{current_row}"] = "-"

            # Column T: Reste à inscrire (1) - (2) (empty as indicated in comments)
            sheet[f"T{current_row}"] = "-"

            # Apply formatting to data cells
            for col_num in range(1, 21):  # A to T
                col_letter: str = get_column_letter(col_num)
                cell: Any = sheet[f"{col_letter}{current_row}"]
                cell.font = Font(name="Arial", size=9)
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = Border(
                    left=Side(style="thin"),
                    right=Side(style="thin"),
                    top=Side(style="thin"),
                    bottom=Side(style="thin"),
                )

        self._current_row += len(dairas_communes_df)

        # Store totals for use in totals row
        self._totals = totals

        self._logger.info(f"Added {len(dairas_communes_df)} data rows successfully")

    def _add_totals_row(
        self, sheet: Worksheet, query_results: dict[str, pd.DataFrame]
    ) -> None:
        """Add the totals row at the bottom of the table."""
        self._logger.debug("Adding totals row")

        # Add "Total" label
        sheet[f"A{self._current_row}"] = "Total général"

        # Leave columns B, C empty for totals row
        sheet[f"B{self._current_row}"] = ""
        sheet[f"C{self._current_row}"] = ""

        # Empty columns as per original design
        sheet[f"D{self._current_row}"] = "-"
        sheet[f"E{self._current_row}"] = "-"

        # Totals from data processing
        totals: dict[str, int] = getattr(self, "_totals", {})

        sheet[f"F{self._current_row}"] = totals.get("aides_inscrites", 0)
        sheet[f"G{self._current_row}"] = totals.get("montants_inscrits", 0)

        # Empty columns as per original design
        sheet[f"H{self._current_row}"] = "-"
        sheet[f"I{self._current_row}"] = "-"

        # Previous year cumulative totals
        sheet[f"J{self._current_row}"] = totals.get("cumul_precedent_t1", 0)
        sheet[f"K{self._current_row}"] = totals.get("cumul_precedent_t2", 0)
        sheet[f"L{self._current_row}"] = totals.get("cumul_precedent_t3", 0)
        sheet[f"M{self._current_row}"] = totals.get("cumul_precedent_montant", 0)

        # Current year totals
        sheet[f"N{self._current_row}"] = totals.get("annee_actuelle_t1", 0)
        sheet[f"O{self._current_row}"] = totals.get("annee_actuelle_t2", 0)
        sheet[f"P{self._current_row}"] = totals.get("annee_actuelle_t3", 0)
        sheet[f"Q{self._current_row}"] = totals.get("annee_actuelle_montant", 0)

        # Total cumul
        sheet[f"R{self._current_row}"] = totals.get("cumul_total", 0)

        # Empty columns as per original design
        sheet[f"S{self._current_row}"] = "-"
        sheet[f"T{self._current_row}"] = "-"

        # Apply bold formatting to totals row
        for col_num in range(1, 21):  # A to T
            col_letter: str = get_column_letter(col_num)
            cell: Any = sheet[f"{col_letter}{self._current_row}"]
            cell.font = Font(name="Arial", size=9, bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = Border(
                left=Side(style="thin"),
                right=Side(style="thin"),
                top=Side(style="thin"),
                bottom=Side(style="thin"),
            )

        self._logger.info("Totals row added successfully")
        self._current_row += 1

    def _finalize_formatting(self, sheet: Worksheet) -> None:
        """Apply final formatting to the worksheet."""
        self._logger.debug("Applying final formatting")

        # Set column widths for better readability
        column_widths: dict[str, int] = {
            "A": 30,  # Programme
            "B": 20,  # Daira
            "C": 25,  # Commune
            "D": 12,  # Aides notifiées
            "E": 15,  # Montants notifiés
            "F": 12,  # Aides inscrites
            "G": 15,  # Montants inscrits
            "H": 12,  # Aides inscrites (2)
            "I": 15,  # Montants inscrits (3)
            "J": 8,  # T1 (prev)
            "K": 8,  # T2 (prev)
            "L": 8,  # T3 (prev)
            "M": 15,  # Montant (4)
            "N": 8,  # T1 (curr)
            "O": 8,  # T2 (curr)
            "P": 8,  # T3 (curr)
            "Q": 15,  # Montant (5)
            "R": 15,  # Cumul
            "S": 20,  # Solde
            "T": 20,  # Reste
        }

        for col, width in column_widths.items():
            sheet.column_dimensions[col].width = width

        # Page setup for landscape orientation
        sheet.page_setup.orientation = "landscape"
        sheet.page_setup.fitToWidth = 1
        sheet.page_setup.fitToHeight = 0

        # Set print area and margins
        sheet.page_margins.left = 0.25
        sheet.page_margins.right = 0.25
        sheet.page_margins.top = 0.75
        sheet.page_margins.bottom = 0.75

        self._logger.info("Final formatting completed successfully")
