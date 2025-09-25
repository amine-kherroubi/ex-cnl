from __future__ import annotations

# Standard library imports
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Third-party imports
import pandas as pd
from openpyxl.worksheet.worksheet import Worksheet

# Local application imports
from app.core.domain.models.subprogram import Subprogram
from app.core.domain.models.notification import Notification
from app.core.domain.models.report_context import ReportContext
from app.core.domain.models.report_specification import ReportSpecification
from app.core.domain.predefined_objects.subprograms import (
    SUBPROGRAMS,
    get_subprograms_dataframe,
)
from app.core.domain.predefined_objects.dairas_et_communes import (
    get_dairas_communes_dataframe,
)
from app.core.infrastructure.data.data_repository import DataRepository
from app.core.infrastructure.file_io.file_io_service import FileIOService
from app.core.services.report_generation_service.base_generator import BaseGenerator
from app.core.services.excel_styling_service import ExcelStylingService


class SituationFinanciereGenerator(BaseGenerator):
    __slots__ = (
        "_current_row",
        "_target_subprogram",
        "_target_notification",
        "_totals",
    )

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
        self._target_subprogram: Subprogram | None = None
        self._target_notification: Notification | None = None
        self._totals: Dict[str, int] = {}

    def configure(self, **kwargs: Any) -> None:
        subprogram_name: str | None = kwargs.get("target_subprogram")
        notification_name: str | None = kwargs.get("target_notification")

        if subprogram_name is None:
            raise ValueError("additional parameter 'target_subprogram' is required")

        if notification_name is None:
            raise ValueError("additional parameter 'target_notification' is required")

        self._logger.debug(f"Setting target subprogram: {subprogram_name}")
        self._logger.debug(f"Setting target notification: {notification_name}")

        # Find the target subprogram
        for subprogram in SUBPROGRAMS:
            if subprogram.name == subprogram_name:
                self._target_subprogram = subprogram
                self._logger.info(f"Target subprogram set: {subprogram.name}")

                # Find the target notification within the subprogram
                for notification in subprogram.notifications:
                    if notification.name == notification_name:
                        self._target_notification = notification
                        self._logger.info(
                            f"Target notification set: {notification.name} "
                            f"(aid_amount: {notification.aid_amount}, aid_count: {notification.aid_count})"
                        )
                        return

                # If notification not found in the subprogram
                available_notifications = [n.name for n in subprogram.notifications]
                error_msg = (
                    f"Notification '{notification_name}' not found in subprogram '{subprogram_name}'. "
                    f"Available notifications: {available_notifications}"
                )
                self._logger.error(error_msg)
                raise ValueError(error_msg)

        # If subprogram not found
        available_subprograms: List[str] = [p.name for p in SUBPROGRAMS]
        error_msg: str = (
            f"Subprogram '{subprogram_name}' not found. "
            f"Available subprograms: {available_subprograms}"
        )
        self._logger.error(error_msg)
        raise ValueError(error_msg)

    def _verify_target_selection(self) -> None:
        if self._target_subprogram is None:
            error_msg: str = (
                "No target subprogram set. Please call configure() with target_subprogram "
                "before generating the report."
            )
            self._logger.error(error_msg)
            raise RuntimeError(error_msg)

        if self._target_notification is None:
            error_msg: str = (
                "No target notification set. Please call configure() with target_notification "
                "before generating the report."
            )
            self._logger.error(error_msg)
            raise RuntimeError(error_msg)

        self._logger.debug(
            f"Target selection verified: {self._target_subprogram.name} - {self._target_notification.name}"
        )

    def generate(
        self,
        source_file_paths: Dict[str, Path],
        output_directory_path: Path,
    ) -> Path:
        self._verify_target_selection()
        return super().generate(source_file_paths, output_directory_path)

    def _create_predefined_tables(self) -> None:
        self._logger.debug("Creating reference tables")

        try:
            self._logger.debug("Creating reference table 'subprograms'")
            df: pd.DataFrame = get_subprograms_dataframe()
            self._data_repository.create_table_from_dataframe("subprograms", df)
            rows, cols = df.shape
            self._logger.info(
                f"Reference table 'subprograms' created: {rows} rows and {cols} columns"
            )
        except Exception as error:
            self._logger.exception(
                f"Failed to create reference table 'subprograms': {error}"
            )
            raise

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
        self._logger.debug("Formatting query template with report context")

        formatted_query: str = query_template

        formatted_query = (
            formatted_query.replace("{subprogram}", f"'{self._target_subprogram.name}'")  # type: ignore
            .replace("{notification}", f"'{self._target_notification.name}'")  # type: ignore
            .replace("{aid_amount}", str(self._target_notification.aid_amount))  # type: ignore
            .replace("{year}", str(self._report_context.year))
            .replace("{month}", str(self._report_context.month.number))
        )

        self._logger.debug(
            f"Placeholders replaced with: month={self._report_context.month.number}, "
            f"year={self._report_context.year}, "
            f"subprogram={self._target_subprogram.name}, "  # type: ignore
            f"notification={self._target_notification.name}, "  # type: ignore
            f"aid_amount={self._target_notification.aid_amount}"  # type: ignore
        )

        self._logger.debug("Query formatting completed")
        return formatted_query

    def _add_content(
        self, sheet: Worksheet, query_results: Dict[str, pd.DataFrame]
    ) -> None:
        self._add_header(sheet)
        self._add_table_headers(sheet)
        self._add_data_rows(sheet, query_results)
        self._add_totals_row(sheet, query_results)

    def _add_header(self, sheet: Worksheet) -> None:
        self._logger.debug("Adding report header")

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "A",
            "T",
            self._current_row,
            self._current_row,
            value=(
                f"Situation financière du sous-programme '{self._target_subprogram.name}'"  # type: ignore
                f"- Notification '{self._target_notification.name}' par daira et par commune",  # type: ignore
            ),
            font=ExcelStylingService.FONT_TITLE,
            alignment=ExcelStylingService.ALIGNMENT_CENTER,
        )

        self._current_row += 1

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "A",
            "T",
            self._current_row,
            self._current_row,
            value=f"Arrêté au {self._report_context.reporting_date.strftime('%d/%m/%Y')}",
            font=ExcelStylingService.FONT_HEADER,
            alignment=ExcelStylingService.ALIGNMENT_CENTER,
        )

        self._current_row += 1

        ExcelStylingService.apply_style_to_cell(
            sheet,
            "A",
            self._current_row,
            font=ExcelStylingService.FONT_HEADER,
            alignment=ExcelStylingService.ALIGNMENT_CENTER,
            value=f"DL de {self._report_context.wilaya.value}",
        )

        self._current_row += 2

        self._logger.info("Report header added successfully")

    def _add_table_headers(self, sheet: Worksheet) -> None:
        self._logger.debug("Adding table headers")

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "F",
            "G",
            self._current_row,
            self._current_row,
            value="Engagement par la BNH",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
            border=ExcelStylingService.BORDER_THIN,
        )

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "H",
            "I",
            self._current_row,
            self._current_row,
            value="Engagement par le MHUV",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
            border=ExcelStylingService.BORDER_THIN,
        )

        self._current_row += 1
        header_start_row: int = self._current_row
        header_end_row: int = self._current_row + 3

        main_headers: List[Tuple[str, str]] = [
            ("A", "Sous-programme"),
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
            ExcelStylingService.merge_and_style_cells(
                sheet,
                col,
                col,
                header_start_row,
                header_end_row,
                value=title,
                font=ExcelStylingService.FONT_BOLD,
                alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
                border=ExcelStylingService.BORDER_THIN,
            )

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "J",
            "Q",
            self._current_row,
            self._current_row,
            value="Consommations",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
            border=ExcelStylingService.BORDER_THIN,
        )

        self._current_row += 1

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "J",
            "M",
            self._current_row,
            self._current_row,
            value=f"Cumuls au 31/12/{self._report_context.year - 1}",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
            border=ExcelStylingService.BORDER_THIN,
        )

        end_day: int = (
            self._report_context.month.last_day(self._report_context.year)
            if not self._report_context.month.is_current
            else date.today().day
        )

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "N",
            "Q",
            self._current_row,
            self._current_row,
            value=f"Du 1 janvier {self._report_context.year} au {end_day} {self._report_context.month.value}",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
            border=ExcelStylingService.BORDER_THIN,
        )

        self._current_row += 1

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "J",
            "L",
            self._current_row,
            self._current_row,
            value="Aides",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
            border=ExcelStylingService.BORDER_THIN,
        )

        ExcelStylingService.apply_style_to_cell(
            sheet,
            "M",
            self._current_row,
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
            border=ExcelStylingService.BORDER_THIN,
            value="Montant (4)",
        )

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "N",
            "P",
            self._current_row,
            self._current_row,
            value="Aides",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
            border=ExcelStylingService.BORDER_THIN,
        )

        ExcelStylingService.apply_style_to_cell(
            sheet,
            "Q",
            self._current_row,
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
            border=ExcelStylingService.BORDER_THIN,
            value="Montant (5)",
        )

        self._current_row += 1

        tranche_headers: List[Tuple[str, str]] = [
            ("J", "T1"),
            ("K", "T2"),
            ("L", "T3"),
            ("N", "T1"),
            ("O", "T2"),
            ("P", "T3"),
        ]

        for col, title in tranche_headers:
            ExcelStylingService.apply_style_to_cell(
                sheet,
                col,
                self._current_row,
                font=ExcelStylingService.FONT_BOLD,
                alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
                border=ExcelStylingService.BORDER_THIN,
                value=title,
            )

        self._current_row += 1
        self._logger.info("Table headers added successfully")

    def _add_data_rows(
        self, sheet: Worksheet, query_results: Dict[str, pd.DataFrame]
    ) -> None:
        self._logger.debug("Adding data rows")

        dairas_communes_df: pd.DataFrame = get_dairas_communes_dataframe()

        data_dicts: Dict[str, Dict[Tuple[str, str], Tuple[int, ...]]] = (
            self._create_lookup_dictionaries(query_results)
        )

        totals: Dict[str, int] = {
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

        for i, (_, row) in enumerate(dairas_communes_df.iterrows()):
            daira: str = row["Daira"]
            commune: str = row["Commune"]
            current_row: int = self._current_row + i

            self._add_single_data_row(
                sheet, current_row, daira, commune, data_dicts, totals
            )

        self._current_row += len(dairas_communes_df)

        self._totals = totals

        self._logger.info(f"Added {len(dairas_communes_df)} data rows successfully")

    def _create_lookup_dictionaries(
        self, query_results: Dict[str, pd.DataFrame]
    ) -> Dict[str, Dict[Tuple[str, str], Tuple[int, ...]]]:
        data_dicts: Dict[str, Dict[Tuple[str, str], Tuple[int, ...]]] = {
            "aides_inscrites": {},
            "cumul_precedent": {},
            "annee_actuelle": {},
        }

        if "nb_aides_et_montants_inscrits_par_daira_et_commune" in query_results:
            df = query_results["nb_aides_et_montants_inscrits_par_daira_et_commune"]
            for _, row in df.iterrows():
                key = (row["Daira du projet"], row["Commune du projet"])
                data_dicts["aides_inscrites"][key] = (
                    row["nb_aides_inscrites"],
                    row["montant_inscrits"],
                )

        if "consommations_cumulees_fin_annee_precedente" in query_results:
            df = query_results["consommations_cumulees_fin_annee_precedente"]
            for _, row in df.iterrows():
                key = (row["Daira"], row["Commune de projet"])
                data_dicts["cumul_precedent"][key] = (
                    row["t_1"],
                    row["t_2"],
                    row["t_3"],
                    row["montant"],
                )

        if "consommations_annee_actuelle_jusqua_mois_actuel" in query_results:
            df = query_results["consommations_annee_actuelle_jusqua_mois_actuel"]
            for _, row in df.iterrows():
                key = (row["Daira"], row["Commune de projet"])
                data_dicts["annee_actuelle"][key] = (
                    row["t_1"],
                    row["t_2"],
                    row["t_3"],
                    row["montant"],
                )

        return data_dicts

    def _add_single_data_row(
        self,
        sheet: Worksheet,
        row: int,
        daira: str,
        commune: str,
        data_dicts: Dict[str, Dict[Tuple[str, str], Tuple[int, ...]]],
        totals: Dict[str, int],
    ) -> None:
        key: Tuple[str, str] = (daira, commune)

        basic_values: List[Tuple[str, Any]] = [
            ("A", f"{self._target_subprogram.name} - {self._target_notification.name}"),  # type: ignore
            ("B", daira),
            ("C", commune),
            ("D", "-"),
            ("E", "-"),
        ]

        if key in data_dicts["aides_inscrites"]:
            aides_data = data_dicts["aides_inscrites"][key]
            aides, montants = aides_data[0], aides_data[1]
            basic_values.extend(
                [
                    ("F", aides if aides > 0 else "-"),
                    ("G", montants if montants > 0 else "-"),
                ]
            )
            totals["aides_inscrites"] += aides
            totals["montants_inscrits"] += montants
        else:
            basic_values.extend([("F", "-"), ("G", "-")])

        basic_values.extend([("H", "-"), ("I", "-")])

        ExcelStylingService.apply_data_row_styling(
            sheet,
            row,
            basic_values,
            font=ExcelStylingService.FONT_NORMAL,
            alignment=ExcelStylingService.ALIGNMENT_CENTER,
            border=ExcelStylingService.BORDER_THIN,
        )

        self._add_cumulative_data(
            sheet,
            row,
            key,
            data_dicts["cumul_precedent"],
            ["J", "K", "L", "M"],
            totals,
            [
                "cumul_precedent_t1",
                "cumul_precedent_t2",
                "cumul_precedent_t3",
                "cumul_precedent_montant",
            ],
        )

        self._add_cumulative_data(
            sheet,
            row,
            key,
            data_dicts["annee_actuelle"],
            ["N", "O", "P", "Q"],
            totals,
            [
                "annee_actuelle_t1",
                "annee_actuelle_t2",
                "annee_actuelle_t3",
                "annee_actuelle_montant",
            ],
        )

        cumul_total = self._calculate_cumul_total(key, data_dicts)
        ExcelStylingService.apply_style_to_cell(
            sheet,
            "R",
            row,
            font=ExcelStylingService.FONT_NORMAL,
            alignment=ExcelStylingService.ALIGNMENT_CENTER,
            border=ExcelStylingService.BORDER_THIN,
            value=cumul_total if cumul_total > 0 else "-",
        )
        totals["cumul_total"] += cumul_total

        final_columns: List[Tuple[str, str]] = [("S", "-"), ("T", "-")]
        ExcelStylingService.apply_data_row_styling(
            sheet,
            row,
            final_columns,
            font=ExcelStylingService.FONT_NORMAL,
            alignment=ExcelStylingService.ALIGNMENT_CENTER,
            border=ExcelStylingService.BORDER_THIN,
        )

    def _add_cumulative_data(
        self,
        sheet: Worksheet,
        row: int,
        key: Tuple[str, str],
        data_dict: Dict[Tuple[str, str], Tuple[int, ...]],
        columns: List[str],
        totals: Dict[str, int],
        total_keys: List[str],
    ) -> None:
        if key in data_dict:
            values = data_dict[key]
            column_data: List[Tuple[str, Any]] = []
            for i, (col, total_key) in enumerate(zip(columns, total_keys)):
                value = values[i]
                column_data.append((col, value if value > 0 else "-"))
                totals[total_key] += value

            ExcelStylingService.apply_data_row_styling(
                sheet,
                row,
                column_data,
                font=ExcelStylingService.FONT_NORMAL,
                alignment=ExcelStylingService.ALIGNMENT_CENTER,
                border=ExcelStylingService.BORDER_THIN,
            )
        else:
            column_data = [(col, "-") for col in columns]
            ExcelStylingService.apply_data_row_styling(
                sheet,
                row,
                column_data,
                font=ExcelStylingService.FONT_NORMAL,
                alignment=ExcelStylingService.ALIGNMENT_CENTER,
                border=ExcelStylingService.BORDER_THIN,
            )

    def _calculate_cumul_total(
        self,
        key: Tuple[str, str],
        data_dicts: Dict[str, Dict[Tuple[str, str], Tuple[int, ...]]],
    ) -> int:
        total: int = 0
        if key in data_dicts["cumul_precedent"]:
            total += data_dicts["cumul_precedent"][key][3]  # montant column
        if key in data_dicts["annee_actuelle"]:
            total += data_dicts["annee_actuelle"][key][3]  # montant column
        return total

    def _add_totals_row(
        self, sheet: Worksheet, query_results: Dict[str, pd.DataFrame]
    ) -> None:
        self._logger.debug("Adding totals row")

        total_values: List[Tuple[str, Any]] = [
            ("A", "Total général"),
            ("B", ""),
            ("C", ""),
            ("D", "-"),
            ("E", "-"),
            ("F", self._totals.get("aides_inscrites", 0)),
            ("G", self._totals.get("montants_inscrits", 0)),
            ("H", "-"),
            ("I", "-"),
            ("J", self._totals.get("cumul_precedent_t1", 0)),
            ("K", self._totals.get("cumul_precedent_t2", 0)),
            ("L", self._totals.get("cumul_precedent_t3", 0)),
            ("M", self._totals.get("cumul_precedent_montant", 0)),
            ("N", self._totals.get("annee_actuelle_t1", 0)),
            ("O", self._totals.get("annee_actuelle_t2", 0)),
            ("P", self._totals.get("annee_actuelle_t3", 0)),
            ("Q", self._totals.get("annee_actuelle_montant", 0)),
            ("R", self._totals.get("cumul_total", 0)),
            ("S", "-"),
            ("T", "-"),
        ]

        ExcelStylingService.apply_data_row_styling(
            sheet,
            self._current_row,
            total_values,
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER,
            border=ExcelStylingService.BORDER_THIN,
        )

        self._logger.info("Totals row added successfully")
        self._current_row += 1

    def _finalize_formatting(self, sheet: Worksheet) -> None:
        self._logger.debug("Applying final formatting")

        column_widths: Dict[str, int] = {
            "A": 35,  # Sous-programme - Notification (wider for both names)
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

        ExcelStylingService.set_column_widths(sheet, column_widths)

        self._apply_number_formatting(sheet)

        ExcelStylingService.setup_page_layout(
            sheet,
            orientation="landscape",
            fit_to_width=True,
            fit_to_height=False,
        )

        ExcelStylingService.setup_page_margins(
            sheet,
            left=0.25,
            right=0.25,
            top=0.5,
            bottom=0.5,
        )

        self._logger.info("Final formatting completed successfully")

    def _apply_number_formatting(self, sheet: Worksheet) -> None:
        self._logger.debug("Applying number formatting to monetary columns")

        monetary_columns = ["G", "M", "Q", "R"]  # Montants columns and cumul

        data_start_row = 6  # Adjust based on your header structure
        data_end_row = self._current_row  # Current row after all data has been added

        for col in monetary_columns:
            for row in range(data_start_row, data_end_row):
                cell = sheet[f"{col}{row}"]
                cell.number_format = "#,##0"

        self._logger.info("Number formatting applied to monetary columns")
