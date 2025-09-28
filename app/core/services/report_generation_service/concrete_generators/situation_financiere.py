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
from app.core.services.excel_styling_service import (
    ExcelStylingService,
    CellData,
    RowData,
    MergeData,
    ColumnData,
)


class SituationFinanciereGenerator(BaseGenerator):
    __slots__ = (
        "_current_row",
        "_target_subprogram", 
        "_target_notification",
        "_data_start_row",
        "_dairas_communes_count",
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
        self._data_start_row: int = 0
        self._dairas_communes_count: int = 0

    def configure(self, **kwargs: Any) -> None:
        target_subprogram: Optional[Subprogram] = kwargs.get("target_subprogram")
        target_notification: Optional[Notification] = kwargs.get("target_notification")

        if target_subprogram is None:
            raise ValueError("additional parameter 'target_subprogram' is required")

        if target_notification is None:
            raise ValueError("additional parameter 'target_notification' is required")

        if not SubprogramRegistry.has_subprogram(target_subprogram.name):
            error_msg: str = (
                f"Subprogram '{target_subprogram.name}' not found. "
                f"Available subprograms: {SubprogramRegistry.get_all_subprogram_names()}"
            )
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
            raise ValueError(error_msg)

        self._target_subprogram = target_subprogram
        self._target_notification = target_notification

    def _verify_target_selection(self) -> None:
        if self._target_subprogram is None:
            raise RuntimeError(
                "No target subprogram set. Please call configure() with target_subprogram "
                "before generating the report."
            )

        if self._target_notification is None:
            raise RuntimeError(
                "No target notification set. Please call configure() with target_notification "
                "before generating the report."
            )

    def generate(
        self,
        source_file_paths: Dict[str, Path],
        output_directory_path: Path,
    ) -> Path:
        self._verify_target_selection()
        return super().generate(source_file_paths, output_directory_path)

    def _create_predefined_tables(self) -> None:
        try:
            df: pd.DataFrame = SubprogramRegistry.get_subprograms_dataframe()
            self._data_repository.create_table_from_dataframe("subprograms", df)
        except Exception as error:
            self._logger.exception(f"Failed to create reference table 'subprograms': {error}")
            raise

        try:
            df: pd.DataFrame = get_dairas_communes_dataframe()
            self._data_repository.create_table_from_dataframe("dairas_communes", df)
            self._dairas_communes_count = len(df)
        except Exception as error:
            self._logger.exception(f"Failed to create reference table 'dairas_communes': {error}")
            raise

    def _format_query_with_context(self, query_template: str) -> str:
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

        return (
            formatted_query.replace(
                "{subprogram}", f"'{self._target_subprogram.database_alias}'"  # type: ignore
            )
            .replace("{notification}", notification_value)
            .replace("{year}", str(self._report_context.year))
            .replace("{month}", str(self._report_context.month.number))
        )

    def _add_content(
        self, sheet: Worksheet, query_results: Dict[str, pd.DataFrame]
    ) -> None:
        self._add_header(sheet)
        self._add_table_headers(sheet)
        self._add_data_rows(sheet, query_results)
        self._add_totals_row(sheet)

    def _add_header(self, sheet: Worksheet) -> None:
        subprogram_display: str = (
            "de "
            if self._target_subprogram.name.startswith("Rattrapage")  # type: ignore
            else ""
        ) + self._target_subprogram.name.lower()  # type: ignore

        notification_display: str = (
            "de toutes les notifications"
            if self._target_notification == SubprogramRegistry.ALL_NOTIFICATIONS_OBJECT
            else f"de la notification {self._target_notification.name.lower()}"  # type: ignore
        )

        title: str = (
            f"Situation financière {notification_display} "
            f"du sous-programme {subprogram_display} par daira et par commune"
        )

        ExcelStylingService.batch_merge_and_style_cells(
            sheet,
            [
                MergeData(
                    "A",
                    "S",
                    self._current_row,
                    self._current_row,
                    value=title,
                    font=ExcelStylingService.FONT_BOLD,
                    alignment=ExcelStylingService.ALIGN_CENTER,
                ),
                MergeData(
                    "A",
                    "S",
                    self._current_row + 1,
                    self._current_row + 1,
                    value=f"Arrêté le {self._report_context.reporting_date.strftime('%d/%m/%Y')}",
                    font=ExcelStylingService.FONT_BOLD,
                    alignment=ExcelStylingService.ALIGN_CENTER,
                ),
            ],
        )

        self._current_row += 2

        ExcelStylingService.style_cell(
            sheet,
            CellData(
                "A",
                self._current_row,
                value=f"DL de {self._report_context.wilaya.value}",
                font=ExcelStylingService.FONT_BOLD,
                alignment=ExcelStylingService.ALIGN_CENTER,
            ),
        )
        self._current_row += 2

    def _add_table_headers(self, sheet: Worksheet) -> None:
        ExcelStylingService.batch_merge_and_style_cells(
            sheet,
            [
                MergeData(
                    "E",
                    "F",
                    self._current_row,
                    self._current_row,
                    value="Engagement par la BNH",
                    font=ExcelStylingService.FONT_BOLD,
                    alignment=ExcelStylingService.ALIGN_CENTER_WRAP,
                    border=ExcelStylingService.BORDER_THIN,
                ),
                MergeData(
                    "G",
                    "H",
                    self._current_row,
                    self._current_row,
                    value="Engagement par le MHUV",
                    font=ExcelStylingService.FONT_BOLD,
                    alignment=ExcelStylingService.ALIGN_CENTER_WRAP,
                    border=ExcelStylingService.BORDER_THIN,
                ),
            ],
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

        ExcelStylingService.batch_merge_and_style_cells(
            sheet,
            [
                MergeData(
                    col,
                    col,
                    header_start_row,
                    header_end_row,
                    value=title,
                    font=ExcelStylingService.FONT_BOLD,
                    alignment=ExcelStylingService.ALIGN_CENTER_WRAP,
                    border=ExcelStylingService.BORDER_THIN,
                )
                for col, title in main_headers
            ],
        )

        ExcelStylingService.merge_and_style_cell(
            sheet,
            MergeData(
                "I",
                "P",
                self._current_row,
                self._current_row,
                value="Consommations",
                font=ExcelStylingService.FONT_BOLD,
                alignment=ExcelStylingService.ALIGN_CENTER_WRAP,
                border=ExcelStylingService.BORDER_THIN,
            ),
        )
        self._current_row += 1

        end_day: int = (
            self._report_context.month.last_day(self._report_context.year)
            if not self._report_context.month.is_current
            else date.today().day
        )

        ExcelStylingService.batch_merge_and_style_cells(
            sheet,
            [
                MergeData(
                    "I",
                    "L",
                    self._current_row,
                    self._current_row,
                    value=f"Cumuls au 31/12/{self._report_context.year - 1}",
                    font=ExcelStylingService.FONT_BOLD,
                    alignment=ExcelStylingService.ALIGN_CENTER_WRAP,
                    border=ExcelStylingService.BORDER_THIN,
                ),
                MergeData(
                    "M",
                    "P",
                    self._current_row,
                    self._current_row,
                    value=f"Du 1 janvier {self._report_context.year} au {end_day} {self._report_context.month.value}",
                    font=ExcelStylingService.FONT_BOLD,
                    alignment=ExcelStylingService.ALIGN_CENTER_WRAP,
                    border=ExcelStylingService.BORDER_THIN,
                ),
            ],
        )
        self._current_row += 1

        ExcelStylingService.batch_merge_and_style_cells(
            sheet,
            [
                MergeData(
                    "I",
                    "K",
                    self._current_row,
                    self._current_row,
                    value="Aides",
                    font=ExcelStylingService.FONT_BOLD,
                    alignment=ExcelStylingService.ALIGN_CENTER_WRAP,
                    border=ExcelStylingService.BORDER_THIN,
                ),
                MergeData(
                    "M",
                    "O",
                    self._current_row,
                    self._current_row,
                    value="Aides",
                    font=ExcelStylingService.FONT_BOLD,
                    alignment=ExcelStylingService.ALIGN_CENTER_WRAP,
                    border=ExcelStylingService.BORDER_THIN,
                ),
            ],
        )

        ExcelStylingService.style_row(
            sheet,
            RowData(
                number=self._current_row,
                cells=[
                    CellData(
                        "L",
                        self._current_row,
                        "Montant (4)",
                        ExcelStylingService.FONT_BOLD,
                        ExcelStylingService.ALIGN_CENTER_WRAP,
                        ExcelStylingService.BORDER_THIN,
                    ),
                    CellData(
                        "P",
                        self._current_row,
                        "Montant (5)",
                        ExcelStylingService.FONT_BOLD,
                        ExcelStylingService.ALIGN_CENTER_WRAP,
                        ExcelStylingService.BORDER_THIN,
                    ),
                ],
            ),
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

        ExcelStylingService.style_row(
            sheet,
            RowData(
                number=self._current_row,
                cells=[
                    CellData(
                        col,
                        self._current_row,
                        title,
                        ExcelStylingService.FONT_BOLD,
                        ExcelStylingService.ALIGN_CENTER_WRAP,
                        ExcelStylingService.BORDER_THIN,
                    )
                    for col, title in tranche_headers
                ],
            ),
        )
        self._current_row += 1

    def _add_data_rows(
        self, sheet: Worksheet, query_results: Dict[str, pd.DataFrame]
    ) -> None:
        dairas_communes_df: pd.DataFrame = get_dairas_communes_dataframe()
        data_dicts: Dict[str, Dict[Tuple[str, str], Tuple[int, ...]]] = (
            self._create_lookup_dictionaries(query_results)
        )

        self._data_start_row = self._current_row
        rows: List[RowData] = []

        for i, (_, row) in enumerate(dairas_communes_df.iterrows()):
            daira: str = row["Daira"]
            commune: str = row["Commune"]
            row_number: int = self._current_row + i
            key: Tuple[str, str] = (daira, commune)

            aides_data = data_dicts["aides_inscrites"].get(key, (0, 0))
            cumul_precedent = data_dicts["cumul_precedent"].get(key, (0, 0, 0, 0))
            annee_actuelle = data_dicts["annee_actuelle"].get(key, (0, 0, 0, 0))

            cumul_formula = f"=L{row_number}+P{row_number}"

            cells: List[CellData] = [
                CellData(
                    "A",
                    row_number,
                    daira,
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "B",
                    row_number,
                    commune,
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData("C", row_number, 0, border=ExcelStylingService.BORDER_THIN),
                CellData("D", row_number, 0, border=ExcelStylingService.BORDER_THIN),
                CellData(
                    "E",
                    row_number,
                    aides_data[0],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "F",
                    row_number,
                    aides_data[1],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData("G", row_number, 0, border=ExcelStylingService.BORDER_THIN),
                CellData("H", row_number, 0, border=ExcelStylingService.BORDER_THIN),
                CellData(
                    "I",
                    row_number,
                    cumul_precedent[0],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "J",
                    row_number,
                    cumul_precedent[1],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "K",
                    row_number,
                    cumul_precedent[2],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "L",
                    row_number,
                    cumul_precedent[3],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "M",
                    row_number,
                    annee_actuelle[0],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "N",
                    row_number,
                    annee_actuelle[1],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "O",
                    row_number,
                    annee_actuelle[2],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "P",
                    row_number,
                    annee_actuelle[3],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "Q",
                    row_number,
                    cumul_formula,
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData("R", row_number, 0, border=ExcelStylingService.BORDER_THIN),
                CellData("S", row_number, 0, border=ExcelStylingService.BORDER_THIN),
            ]

            rows.append(RowData(number=row_number, cells=cells))

        ExcelStylingService.batch_style_rows(sheet, rows)
        self._current_row += len(dairas_communes_df)
        self._merge_daira_cells(sheet, dairas_communes_df)

    def _merge_daira_cells(
        self, sheet: Worksheet, dairas_communes_df: pd.DataFrame
    ) -> None:
        current_row: int = self._data_start_row

        while current_row <= self._data_start_row + len(dairas_communes_df) - 1:
            current_daira: str = sheet[f"A{current_row}"].value

            merge_end_row: int = current_row
            while (
                merge_end_row + 1 <= self._data_start_row + len(dairas_communes_df) - 1
                and sheet[f"A{merge_end_row + 1}"].value == current_daira
            ):
                merge_end_row += 1

            if merge_end_row > current_row:
                try:
                    ExcelStylingService.merge_and_style_cells_with_same_value(
                        sheet=sheet,
                        column="A",
                        start_row=current_row,
                        end_row=merge_end_row,
                        font=ExcelStylingService.FONT_NORMAL,
                        alignment=ExcelStylingService.ALIGN_CENTER,
                        border=ExcelStylingService.BORDER_THIN,
                    )
                except ValueError:
                    pass

            current_row = merge_end_row + 1

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

    def _add_totals_row(self, sheet: Worksheet) -> None:
        data_end_row: int = self._current_row - 1
        
        formula_columns: List[str] = ["E", "F", "I", "J", "K", "L", "M", "N", "O", "P", "Q"]
        
        total_cells: List[CellData] = []

        for col in ["C", "D", "G", "H", "R", "S"]:
            total_cells.append(
                CellData(
                    col,
                    self._current_row,
                    0,
                    ExcelStylingService.FONT_BOLD,
                    ExcelStylingService.ALIGN_CENTER,
                    ExcelStylingService.BORDER_THIN,
                )
            )

        for col in formula_columns:
            total_cells.append(
                CellData(
                    col,
                    self._current_row,
                    ExcelStylingService.create_sum_formula(
                        col, self._data_start_row, data_end_row
                    ),
                    ExcelStylingService.FONT_BOLD,
                    ExcelStylingService.ALIGN_CENTER,
                    ExcelStylingService.BORDER_THIN,
                )
            )

        ExcelStylingService.style_row(
            sheet, RowData(number=self._current_row, cells=total_cells)
        )

        ExcelStylingService.merge_and_style_cell(
            sheet,
            MergeData(
                "A",
                "B",
                self._current_row,
                self._current_row,
                value="Total général",
                font=ExcelStylingService.FONT_BOLD,
                alignment=ExcelStylingService.ALIGN_CENTER,
                border=ExcelStylingService.BORDER_THIN,
            ),
        )
        self._current_row += 1

    def _finalize_formatting(self, sheet: Worksheet) -> None:
        column_widths: Dict[str, int] = {
            "A": 20,
            "B": 20,
            "C": 8,
            "D": 12,
            "E": 8,
            "F": 12,
            "G": 8,
            "H": 12,
            "I": 6,
            "J": 6,
            "K": 6,
            "L": 12,
            "M": 6,
            "N": 6,
            "O": 6,
            "P": 12,
            "Q": 12,
            "R": 12,
            "S": 12,
        }

        ExcelStylingService.batch_style_columns(
            sheet,
            [ColumnData(letter, width) for letter, width in column_widths.items()],
        )

        self._apply_number_formatting(sheet)

        ExcelStylingService.set_page_layout(
            sheet, orientation="landscape", fit_to_width=True
        )
        ExcelStylingService.set_page_margins(
            sheet, left=0.25, right=0.25, top=0.5, bottom=0.5
        )

    def _apply_number_formatting(self, sheet: Worksheet) -> None:
        monetary_columns = ["F", "L", "P", "Q", "R"]
        data_end_row: int = self._current_row

        for col in monetary_columns:
            for row in range(self._data_start_row, data_end_row):
                cell = sheet[f"{col}{row}"]
                cell.number_format = "#,##0"