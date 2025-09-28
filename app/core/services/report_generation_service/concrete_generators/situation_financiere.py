# Standard library imports
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

# Third-party imports
import pandas as pd
from openpyxl.worksheet.worksheet import Worksheet

# Local application imports
from app.core.domain.models.subprogram import Subprogram
from app.core.domain.models.notification import Notification
from app.core.domain.models.report_context import ReportContext
from app.core.domain.models.report_specification import ReportSpecification
from app.core.domain.registries.subprogram_registry import SubprogramRegistry
from app.core.domain.predefined_objects.dairas_et_communes import (
    get_dairas_communes_dataframe,
)
from app.core.infrastructure.data.data_repository import DataRepository
from app.core.infrastructure.file_io.file_io_service import FileIOService
from app.core.services.report_generation_service.base_report_generator import (
    BaseGenerator,
)
from app.core.services.excel_styling_service import ExcelStylingService


class SituationFinanciereGenerator(BaseGenerator):
    __slots__ = (
        "_current_row",
        "_target_subprogram",
        "_target_notification",
        "_totals",
        "_data_start_row",
        "_data_end_row",
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
        self._target_subprogram: Optional[Subprogram] = None
        self._target_notification: Optional[Notification] = None
        self._totals: Dict[str, int] = {}
        self._data_start_row: int = 0
        self._data_end_row: int = 0

    def configure(self, **kwargs: Any) -> None:
        target_subprogram: Optional[Subprogram] = kwargs.get("target_subprogram")
        target_notification: Optional[Notification] = kwargs.get("target_notification")

        if target_subprogram is None:
            raise ValueError("additional parameter 'target_subprogram' is required")

        if target_notification is None:
            raise ValueError("additional parameter 'target_notification' is required")

        self._logger.debug(f"Setting target subprogram: {target_subprogram}")
        self._logger.debug(f"Setting target notification: {target_notification}")

        if not SubprogramRegistry.has_subprogram(target_subprogram.name):
            error_msg: str = (
                f"Subprogram '{target_subprogram.name}' not found. "
                f"Available subprograms: {SubprogramRegistry.get_all_subprogram_names()}"
            )
            self._logger.error(error_msg)
            raise ValueError(error_msg)

        if (
            target_notification not in target_subprogram.notifications
            and target_notification != SubprogramRegistry.ALL_NOTIFICATIONS_OBJECT
        ):
            available_notifications: List[Notification] = [
                notification for notification in target_subprogram.notifications
            ]
            error_msg: str = (
                f"Notification '{target_notification.name}' not found. "
                f"Available notifications: {available_notifications}"
            )
            self._logger.error(error_msg)
            raise ValueError(error_msg)

        self._target_subprogram = target_subprogram
        self._logger.info(f"Target subprogram set: {target_subprogram.database_alias}")

        self._target_notification = target_notification
        self._logger.info(
            f"Target notification set: {target_notification.name} "
            f"(aid_amount: {target_notification.aid_amount}, aid_count: {target_notification.aid_count})"
        )

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
            df: pd.DataFrame = SubprogramRegistry.get_subprograms_dataframe()
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

        if self._target_notification == SubprogramRegistry.ALL_NOTIFICATIONS_OBJECT:
            notification_value: str = ", ".join(
                f"'{alias}'"
                for notification in self._target_subprogram.notifications  # type: ignore
                for alias in notification.database_aliases
            )
        else:
            aliases: list[str] = self._target_notification.database_aliases  # type: ignore
            if len(aliases) == 1:
                notification_value: str = f"'{aliases[0]}'"
            else:
                notification_value: str = ", ".join(f"'{alias}'" for alias in aliases)

        formatted_query = (
            formatted_query.replace(
                "{subprogram}", f"'{self._target_subprogram.database_alias}'"  # type: ignore
            )
            .replace("{notification}", notification_value)
            .replace("{year}", str(self._report_context.year))
            .replace("{month}", str(self._report_context.month.number))
        )

        self._logger.debug(
            f"Placeholders replaced with: month={self._report_context.month.number}, "
            f"year={self._report_context.year}, "
            f"subprogram={self._target_subprogram.database_alias}, "  # type: ignore
            f"notification={self._target_notification.database_aliases}, "  # type: ignore
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

        subprogram_display: str = (
            "de "
            if self._target_subprogram.name.startswith("Rattrapage")  # type: ignore
            else ""
        ) + self._target_subprogram.name.lower()  # type: ignore
        notification_display: str = self._target_notification.name.lower()  # type: ignore

        notification_display: str = (
            "de toutes les notifications"
            if self._target_notification == SubprogramRegistry.ALL_NOTIFICATIONS_OBJECT
            else f"de la notification {self._target_notification.name.lower()}"  # type: ignore
        )

        title: str = (
            f"Situation financière {notification_display} "
            f"du sous-programme {subprogram_display} par daira et par commune"
        )

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "A",
            "S",
            self._current_row,
            self._current_row,
            value=title,
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER,
        )

        self._current_row += 1

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "A",
            "S",
            self._current_row,
            self._current_row,
            value=f"Arrêté le {self._report_context.reporting_date.strftime('%d/%m/%Y')}",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER,
        )

        self._current_row += 1

        ExcelStylingService.apply_style_to_cell(
            sheet,
            "A",
            self._current_row,
            value=f"DL de {self._report_context.wilaya.value}",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER,
        )

        self._current_row += 2

        self._logger.info("Report header added successfully")

    def _add_table_headers(self, sheet: Worksheet) -> None:
        self._logger.debug("Adding table headers")

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "E",
            "F",
            self._current_row,
            self._current_row,
            value="Engagement par la BNH",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
            border=ExcelStylingService.BORDER_THIN,
        )

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "G",
            "H",
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
            ("A", "Daira"),
            ("B", "Commune"),
            ("C", "Aides notifiées\n(1)"),
            ("D", "Montants notifiés"),
            ("E", "Aides inscrites"),
            ("F", "Montants inscrits"),
            ("G", "Aides inscrites\n(2)"),
            ("H", "Montants inscrits\n(3)"),
            ("Q", "Cumul\n(6) = (4) + (5)"),
            ("R", "Solde sur engagement\n(3) - (6)"),
            ("S", "Reste à inscrire\n(1) - (2)"),
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
            "I",
            "P",
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
            "I",
            "L",
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
            "M",
            "P",
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
            "I",
            "K",
            self._current_row,
            self._current_row,
            value="Aides",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
            border=ExcelStylingService.BORDER_THIN,
        )

        ExcelStylingService.apply_style_to_cell(
            sheet,
            "L",
            self._current_row,
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
            border=ExcelStylingService.BORDER_THIN,
            value="Montant (4)",
        )

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "M",
            "O",
            self._current_row,
            self._current_row,
            value="Aides",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
            border=ExcelStylingService.BORDER_THIN,
        )

        ExcelStylingService.apply_style_to_cell(
            sheet,
            "P",
            self._current_row,
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
            border=ExcelStylingService.BORDER_THIN,
            value="Montant (5)",
        )

        self._current_row += 1

        tranche_headers: List[Tuple[str, str]] = [
            ("I", "T1"),
            ("J", "T2"),
            ("K", "T3"),
            ("M", "T1"),
            ("N", "T2"),
            ("O", "T3"),
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

        # Store the start row for merging later
        self._data_start_row = self._current_row

        for i, (_, row) in enumerate(dairas_communes_df.iterrows()):
            daira: str = row["Daira"]
            commune: str = row["Commune"]
            current_row: int = self._current_row + i

            self._add_single_data_row(
                sheet, current_row, daira, commune, data_dicts, totals
            )

        self._data_end_row = self._current_row + len(dairas_communes_df) - 1
        self._current_row += len(dairas_communes_df)

        # Apply merging to daira column (column A) for consecutive identical values
        self._merge_daira_cells(sheet, dairas_communes_df)

        self._totals = totals

        self._logger.info(f"Added {len(dairas_communes_df)} data rows successfully")

    def _merge_daira_cells(
        self, sheet: Worksheet, dairas_communes_df: pd.DataFrame
    ) -> None:
        """
        Merge consecutive daira cells that have identical content.
        """
        self._logger.debug("Merging daira cells")

        current_row: int = self._data_start_row

        while current_row <= self._data_end_row:
            current_daira: str = sheet[f"A{current_row}"].value

            # Find the end of consecutive identical daira values
            merge_end_row: int = current_row
            while (
                merge_end_row + 1 <= self._data_end_row
                and sheet[f"A{merge_end_row + 1}"].value == current_daira
            ):
                merge_end_row += 1

            # If we have more than one cell with the same daira value, merge them
            if merge_end_row > current_row:
                try:
                    ExcelStylingService.merge_cells_with_same_content(
                        sheet=sheet,
                        col="A",
                        start_row=current_row,
                        end_row=merge_end_row,
                        font=ExcelStylingService.FONT_NORMAL,
                        alignment=ExcelStylingService.ALIGNMENT_CENTER,
                        border=ExcelStylingService.BORDER_THIN,
                    )
                    self._logger.debug(
                        f"Merged daira '{current_daira}' from row {current_row} to {merge_end_row}"
                    )
                except ValueError as e:
                    self._logger.warning(f"Failed to merge daira cells: {e}")
            else:
                # Apply styling to single cell
                ExcelStylingService.apply_style_to_cell(
                    sheet=sheet,
                    col="A",
                    row=current_row,
                    font=ExcelStylingService.FONT_NORMAL,
                    alignment=ExcelStylingService.ALIGNMENT_CENTER,
                    border=ExcelStylingService.BORDER_THIN,
                )

            current_row = merge_end_row + 1

        self._logger.info("Daira cell merging completed successfully")

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

        # Note: We don't style column A (daira) here since it will be handled by the merge function
        basic_values: List[Tuple[str, Any]] = [
            ("B", commune),
            ("C", "-"),
            ("D", "-"),
        ]

        # Set the daira value directly without styling (will be styled during merge)
        sheet[f"A{row}"].value = daira

        if key in data_dicts["aides_inscrites"]:
            aides_data = data_dicts["aides_inscrites"][key]
            aides, montants = aides_data[0], aides_data[1]
            basic_values.extend(
                [
                    ("E", aides if aides > 0 else "-"),
                    ("F", montants if montants > 0 else "-"),
                ]
            )
            totals["aides_inscrites"] += aides
            totals["montants_inscrits"] += montants
        else:
            basic_values.extend([("E", "-"), ("F", "-")])

        basic_values.extend([("G", "-"), ("H", "-")])

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
            ["I", "J", "K", "L"],
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
            ["M", "N", "O", "P"],
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
            "Q",
            row,
            font=ExcelStylingService.FONT_NORMAL,
            alignment=ExcelStylingService.ALIGNMENT_CENTER,
            border=ExcelStylingService.BORDER_THIN,
            value=cumul_total if cumul_total > 0 else "-",
        )
        totals["cumul_total"] += cumul_total

        final_columns: List[Tuple[str, str]] = [("R", "-"), ("S", "-")]
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
            ("A", ""),
            ("B", ""),
            ("C", "-"),
            ("D", "-"),
            ("E", self._totals.get("aides_inscrites", 0)),
            ("F", self._totals.get("montants_inscrits", 0)),
            ("G", "-"),
            ("H", "-"),
            ("I", self._totals.get("cumul_precedent_t1", 0)),
            ("J", self._totals.get("cumul_precedent_t2", 0)),
            ("K", self._totals.get("cumul_precedent_t3", 0)),
            ("L", self._totals.get("cumul_precedent_montant", 0)),
            ("M", self._totals.get("annee_actuelle_t1", 0)),
            ("N", self._totals.get("annee_actuelle_t2", 0)),
            ("O", self._totals.get("annee_actuelle_t3", 0)),
            ("P", self._totals.get("annee_actuelle_montant", 0)),
            ("Q", self._totals.get("cumul_total", 0)),
            ("R", "-"),
            ("S", "-"),
        ]

        ExcelStylingService.apply_data_row_styling(
            sheet,
            self._current_row,
            total_values,
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER,
            border=ExcelStylingService.BORDER_THIN,
        )

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "A",
            "B",
            self._current_row,
            self._current_row,
            value="Total général",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER,
            border=ExcelStylingService.BORDER_THIN,
        )

        self._logger.info("Totals row added successfully")
        self._current_row += 1

    def _finalize_formatting(self, sheet: Worksheet) -> None:
        self._logger.debug("Applying final formatting")

        column_widths: Dict[str, int] = {
            "A": 20,  # Daira
            "B": 20,  # Commune
            "C": 8,  # Aides notifiées
            "D": 12,  # Montants notifiés
            "E": 8,  # Aides inscrites
            "F": 12,  # Montants inscrits
            "G": 8,  # Aides inscrites (2)
            "H": 12,  # Montants inscrits (3)
            "I": 6,  # T1 (prev)
            "J": 6,  # T2 (prev)
            "K": 6,  # T3 (prev)
            "L": 12,  # Montant (4)
            "M": 6,  # T1 (curr)
            "N": 6,  # T2 (curr)
            "O": 6,  # T3 (curr)
            "P": 12,  # Montant (5)
            "Q": 12,  # Cumul
            "R": 12,  # Solde
            "S": 12,  # Reste
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
        self._logger.debug("Applying French number formatting to monetary columns")

        monetary_columns = ["F", "L", "P", "Q", "R"]

        data_start_row: int = 6
        data_end_row: int = (
            self._current_row
        )  # Current row after all data has been added

        for col in monetary_columns:
            for row in range(data_start_row, data_end_row):
                cell: Any = sheet[f"{col}{row}"]
                # French number format with space as thousands separator
                cell.number_format = "#,##0"

        self._logger.info("French number formatting applied to monetary columns")
