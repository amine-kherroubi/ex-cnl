# Standard library imports
from datetime import date
from typing import Any, Dict, List, Tuple

# Third-party imports
import pandas as pd
from openpyxl.worksheet.worksheet import Worksheet

# Local application imports
from app.core.domain.models.report_context import ReportContext
from app.core.domain.models.report_specification import ReportSpecification
from app.core.domain.models.subprogram import Subprogram
from app.core.domain.registries.subprogram_registry import SubprogramRegistry
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


class SituationParSousProgrammeGenerator(BaseGenerator):
    __slots__ = ("_current_row", "_data_start_row", "_subprograms_count")

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
        self._data_start_row: int = 0
        self._subprograms_count: int = 0

    def configure(self, **kwargs: Any) -> None:
        if kwargs:
            self._logger.debug(
                f"Ignoring unused configuration parameters: {list(kwargs.keys())}"
            )

    def _create_predefined_tables(self) -> None:
        try:
            df: pd.DataFrame = SubprogramRegistry.get_subprograms_dataframe()
            self._data_repository.create_table_from_dataframe("subprograms", df)
            self._subprograms_count = len(df)
        except Exception as error:
            self._logger.exception(f"Failed to create reference table: {error}")
            raise

    def _format_query_with_context(self, query_template: str) -> str:
        return query_template.format(
            month=self._report_context.month.number, year=self._report_context.year
        )

    def _add_content(
        self, sheet: Worksheet, query_results: Dict[str, pd.DataFrame]
    ) -> None:
        self._add_header(sheet)
        self._add_table_headers(sheet)
        self._add_data_rows(sheet, query_results)
        self._add_totals_row(sheet)

    def _add_header(self, sheet: Worksheet) -> None:
        ExcelStylingService.merge_and_style_cell(
            sheet,
            MergeData(
                "A",
                "R",
                self._current_row,
                self._current_row,
                value="Situation financière par sous-programme",
                font=ExcelStylingService.FONT_BOLD,
                alignment=ExcelStylingService.ALIGN_CENTER,
            ),
        )
        self._current_row += 1

        ExcelStylingService.merge_and_style_cell(
            sheet,
            MergeData(
                "A",
                "R",
                self._current_row,
                self._current_row,
                value=f"Arrêté le {self._report_context.reporting_date.strftime('%d/%m/%Y')}",
                font=ExcelStylingService.FONT_BOLD,
                alignment=ExcelStylingService.ALIGN_CENTER,
            ),
        )
        self._current_row += 1

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
                    "D",
                    "E",
                    self._current_row,
                    self._current_row,
                    value="Engagement par la BNH",
                    font=ExcelStylingService.FONT_BOLD,
                    alignment=ExcelStylingService.ALIGN_CENTER_WRAP,
                    border=ExcelStylingService.BORDER_THIN,
                ),
                MergeData(
                    "F",
                    "G",
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
            ("A", "Sous-programme"),
            ("B", "Aides notifiées\n(1)"),
            ("C", "Montants notifiés"),
            ("D", "Aides inscrites"),
            ("E", "Montants inscrits"),
            ("F", "Aides inscrites\n(2)"),
            ("G", "Montants inscrits\n(3)"),
            ("P", "Cumul\n(6) = (4) + (5)"),
            ("Q", "Solde sur engagement\n(3) - (6)"),
            ("R", "Reste à inscrire\n(1) - (2)"),
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
                "H",
                "O",
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
                    "H",
                    "K",
                    self._current_row,
                    self._current_row,
                    value=f"Cumuls au 31/12/{self._report_context.year - 1}",
                    font=ExcelStylingService.FONT_BOLD,
                    alignment=ExcelStylingService.ALIGN_CENTER_WRAP,
                    border=ExcelStylingService.BORDER_THIN,
                ),
                MergeData(
                    "L",
                    "O",
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
                    "H",
                    "J",
                    self._current_row,
                    self._current_row,
                    value="Aides",
                    font=ExcelStylingService.FONT_BOLD,
                    alignment=ExcelStylingService.ALIGN_CENTER_WRAP,
                    border=ExcelStylingService.BORDER_THIN,
                ),
                MergeData(
                    "L",
                    "N",
                    self._current_row,
                    self._current_row,
                    value="Aides",
                    font=ExcelStylingService.FONT_BOLD,
                    alignment=ExcelStylingService.ALIGN_CENTER_WRAP,
                    border=ExcelStylingService.BORDER_THIN,
                ),
            ],
        )

        ExcelStylingService.batch_style_rows(
            sheet,
            [
                RowData(
                    number=self._current_row,
                    cells=[
                        CellData(
                            "K",
                            self._current_row,
                            "Montant (4)",
                            ExcelStylingService.FONT_BOLD,
                            ExcelStylingService.ALIGN_CENTER_WRAP,
                            ExcelStylingService.BORDER_THIN,
                        ),
                        CellData(
                            "O",
                            self._current_row,
                            "Montant (5)",
                            ExcelStylingService.FONT_BOLD,
                            ExcelStylingService.ALIGN_CENTER_WRAP,
                            ExcelStylingService.BORDER_THIN,
                        ),
                    ],
                )
            ],
        )
        self._current_row += 1

        tranche_headers: List[Tuple[str, str]] = [
            ("H", "T1"),
            ("I", "T2"),
            ("J", "T3"),
            ("L", "T1"),
            ("M", "T2"),
            ("N", "T3"),
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
        subprograms_df: pd.DataFrame = SubprogramRegistry.get_subprograms_dataframe()
        data_dicts: Dict[str, Dict[str, Tuple[int, ...]]] = (
            self._create_lookup_dictionaries(query_results)
        )

        self._data_start_row = self._current_row
        rows: List[RowData] = []

        for i, (_, row) in enumerate(subprograms_df.iterrows()):
            subprogram: str = row["subprogram"]
            row_number: int = self._current_row + i

            try:
                subprogram_obj: Subprogram = (
                    SubprogramRegistry.get_subprogram_by_database_alias(subprogram)
                )
                display_name: str = subprogram_obj.name
            except ValueError:
                display_name: str = subprogram

            aides_data: Tuple[int, ...] = data_dicts["aides_inscrites"].get(
                subprogram, (0, 0)
            )
            cumul_precedent: Tuple[int, ...] = data_dicts["cumul_precedent"].get(
                subprogram, (0, 0, 0, 0)
            )
            annee_actuelle: Tuple[int, ...] = data_dicts["annee_actuelle"].get(
                subprogram, (0, 0, 0, 0)
            )

            cumul_formula: str = f"=K{row_number}+O{row_number}"
            solde_formula: str = f"=G{row_number}-P{row_number}"
            reste_formula: str = f"=B{row_number}-F{row_number}"

            cells: List[CellData] = [
                CellData(
                    "A",
                    row_number,
                    display_name,
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "B",
                    row_number,
                    aides_data[0],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "C",
                    row_number,
                    aides_data[1],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "D",
                    row_number,
                    aides_data[0],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "E",
                    row_number,
                    aides_data[1],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "F",
                    row_number,
                    aides_data[0],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "G",
                    row_number,
                    aides_data[1],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "H",
                    row_number,
                    cumul_precedent[0],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "I",
                    row_number,
                    cumul_precedent[1],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "J",
                    row_number,
                    cumul_precedent[2],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "K",
                    row_number,
                    cumul_precedent[3],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "L",
                    row_number,
                    annee_actuelle[0],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "M",
                    row_number,
                    annee_actuelle[1],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "N",
                    row_number,
                    annee_actuelle[2],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "O",
                    row_number,
                    annee_actuelle[3],
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "P",
                    row_number,
                    cumul_formula,
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "Q",
                    row_number,
                    solde_formula,
                    border=ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "R",
                    row_number,
                    reste_formula,
                    border=ExcelStylingService.BORDER_THIN,
                ),
            ]

            rows.append(RowData(number=row_number, cells=cells))

        ExcelStylingService.batch_style_rows(sheet, rows)
        self._current_row += len(subprograms_df)

    def _create_lookup_dictionaries(
        self, query_results: Dict[str, pd.DataFrame]
    ) -> Dict[str, Dict[str, Tuple[int, ...]]]:
        data_dicts: Dict[str, Dict[str, Tuple[int, ...]]] = {
            "aides_inscrites": {},
            "cumul_precedent": {},
            "annee_actuelle": {},
        }

        if "nb_aides_et_montants_inscrits_par_sous_programme" in query_results:
            df = query_results["nb_aides_et_montants_inscrits_par_sous_programme"]
            for _, row in df.iterrows():
                key = row["Sous programme"]
                data_dicts["aides_inscrites"][key] = (
                    row["nb_aides_inscrites"],
                    row["montant_inscrits"],
                )

        if "consommations_cumulees_fin_annee_precedente" in query_results:
            df = query_results["consommations_cumulees_fin_annee_precedente"]
            for _, row in df.iterrows():
                key = row["Sous programme"]
                data_dicts["cumul_precedent"][key] = (
                    row["t_1"],
                    row["t_2"],
                    row["t_3"],
                    row["montant"],
                )

        if "consommations_annee_actuelle_jusqua_mois_actuel" in query_results:
            df = query_results["consommations_annee_actuelle_jusqua_mois_actuel"]
            for _, row in df.iterrows():
                key = row["Sous programme"]
                data_dicts["annee_actuelle"][key] = (
                    row["t_1"],
                    row["t_2"],
                    row["t_3"],
                    row["montant"],
                )

        return data_dicts

    def _add_totals_row(self, sheet: Worksheet) -> None:
        data_end_row: int = self._current_row - 1

        formula_columns: List[str] = [
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
        ]

        total_cells: List[CellData] = [
            CellData(
                "A",
                self._current_row,
                "Total général",
                ExcelStylingService.FONT_BOLD,
                ExcelStylingService.ALIGN_CENTER,
                ExcelStylingService.BORDER_THIN,
            )
        ]

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
        self._current_row += 1

    def _finalize_formatting(self, sheet: Worksheet) -> None:
        column_widths: Dict[str, int] = {
            "A": 25,
            "B": 8,
            "C": 12,
            "D": 8,
            "E": 12,
            "F": 8,
            "G": 12,
            "H": 6,
            "I": 6,
            "J": 6,
            "K": 12,
            "L": 6,
            "M": 6,
            "N": 6,
            "O": 12,
            "P": 12,
            "Q": 12,
            "R": 12,
        }

        ExcelStylingService.batch_style_columns(
            sheet,
            [ColumnData(letter, width) for letter, width in column_widths.items()],
        )

        monetary_columns: List[str] = ["C", "E", "G", "K", "O", "P", "Q"]
        ExcelStylingService.format_numbers(
            sheet,
            monetary_columns,
            self._data_start_row,
            self._current_row,
        )

        ExcelStylingService.set_page_layout(
            sheet, orientation="landscape", fit_to_width=True
        )
        ExcelStylingService.set_page_margins(
            sheet, left=0.25, right=0.25, top=0.5, bottom=0.5
        )
