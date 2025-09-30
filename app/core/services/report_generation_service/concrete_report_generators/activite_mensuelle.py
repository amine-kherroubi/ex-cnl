# Standard library imports
from datetime import date
from typing import Any, Dict, List, Tuple

# Third-party imports
import pandas as pd
from openpyxl.worksheet.worksheet import Worksheet

# Local application imports
from app.core.domain.models.report_context import ReportContext
from app.core.domain.models.report_specification import ReportSpecification
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


class ActiviteMensuelleGenerator(BaseGenerator):
    __slots__ = ("_current_row", "_first_data_row", "_subprograms_count")

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
        self._first_data_row: int = 0
        self._subprograms_count: int = 0

    def configure(self, **kwargs: Any) -> None:
        if kwargs:
            self._logger.debug(
                f"Ignoring unused configuration parameters: {list(kwargs.keys())}"
            )

    def _create_predefined_tables(self) -> None:
        self._logger.debug("Creating reference tables")
        try:
            df: pd.DataFrame = SubprogramRegistry.get_subprograms_dataframe()
            self._data_repository.create_table_from_dataframe("subprograms", df)

            self._subprograms_count = len(df)
            self._logger.info(
                f"Reference table 'subprograms' created: {self._subprograms_count} rows and {df.shape[1]} columns"
            )
        except Exception as error:
            self._logger.exception(
                f"Failed to create reference table 'subprograms': {error}"
            )
            raise

    def _format_query_with_context(self, query_template: str) -> str:
        return query_template.format(
            month=self._report_context.month.number, year=self._report_context.year
        )

    def _add_content(
        self, sheet: Worksheet, query_results: Dict[str, pd.DataFrame]
    ) -> None:
        self._add_first_table_header(sheet)
        self._add_first_table(sheet, query_results)
        self._add_second_table_header(sheet)
        self._add_second_table(sheet, query_results)
        self._add_footer(sheet)

    def _add_first_table_header(self, sheet: Worksheet) -> None:
        ExcelStylingService.merge_and_style_cell(
            sheet,
            MergeData(
                "A",
                "E",
                self._current_row,
                self._current_row,
                value="Habitat rural",
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
                value=f"Wilaya de {self._report_context.wilaya.value}",
                font=ExcelStylingService.FONT_BOLD,
                alignment=ExcelStylingService.ALIGN_CENTER,
            ),
        )
        self._current_row += 1

        ExcelStylingService.merge_and_style_cell(
            sheet,
            MergeData(
                "A",
                "E",
                self._current_row,
                self._current_row,
                value="Activité mensuelle par sous-programme (à renseigner par la BNH, ex-CNL)",
                font=ExcelStylingService.FONT_BOLD,
                alignment=ExcelStylingService.ALIGN_CENTER_WRAP,
            ),
        )
        self._current_row += 1

        ExcelStylingService.merge_and_style_cell(
            sheet,
            MergeData(
                "A",
                "E",
                self._current_row,
                self._current_row,
                value=f"Mois de {self._report_context.month.value} {self._report_context.year}",
                font=ExcelStylingService.FONT_BOLD,
                alignment=ExcelStylingService.ALIGN_CENTER,
            ),
        )
        self._current_row += 2

    def _add_first_table(
        self, sheet: Worksheet, query_results: Dict[str, pd.DataFrame]
    ) -> None:
        ExcelStylingService.merge_and_style_cell(
            sheet,
            MergeData(
                "A",
                "A",
                self._current_row,
                self._current_row + 2,
                value="Programme",
                font=ExcelStylingService.FONT_BOLD,
                alignment=ExcelStylingService.ALIGN_CENTER_WRAP,
                border=ExcelStylingService.BORDER_THIN,
            ),
        )

        ExcelStylingService.merge_and_style_cell(
            sheet,
            MergeData(
                "B",
                "E",
                self._current_row,
                self._current_row,
                value=f"État d'exécution des tranches financières durant le mois de {self._report_context.month.value} {self._report_context.year}",
                font=ExcelStylingService.FONT_BOLD,
                alignment=ExcelStylingService.ALIGN_CENTER_WRAP,
                border=ExcelStylingService.BORDER_THIN,
            ),
        )
        self._current_row += 1

        ExcelStylingService.batch_merge_and_style_cells(
            sheet,
            [
                MergeData(
                    "B",
                    "C",
                    self._current_row,
                    self._current_row,
                    value="Livraisons (libération de la dernière tranche)",
                    font=ExcelStylingService.FONT_BOLD,
                    alignment=ExcelStylingService.ALIGN_CENTER_WRAP,
                    border=ExcelStylingService.BORDER_THIN,
                ),
                MergeData(
                    "D",
                    "E",
                    self._current_row,
                    self._current_row,
                    value="Lancements (libération de la première tranche)",
                    font=ExcelStylingService.FONT_BOLD,
                    alignment=ExcelStylingService.ALIGN_CENTER_WRAP,
                    border=ExcelStylingService.BORDER_THIN,
                ),
            ],
        )
        self._current_row += 1

        cumul_text: str = (
            f"Cumul du 1er janvier au "
            f"{self._report_context.month.last_day(self._report_context.year) if not self._report_context.month.is_current else date.today().day} "
            f"{self._report_context.month.value} {self._report_context.year}"
        )
        month_year: str = (
            f"{self._report_context.month.value.capitalize()} {self._report_context.year}"
        )
        ExcelStylingService.style_row(
            sheet,
            RowData(
                number=self._current_row,
                cells=[
                    CellData(
                        "B",
                        self._current_row,
                        month_year,
                        ExcelStylingService.FONT_BOLD,
                        ExcelStylingService.ALIGN_CENTER_WRAP,
                        ExcelStylingService.BORDER_THIN,
                    ),
                    CellData(
                        "C",
                        self._current_row,
                        cumul_text,
                        ExcelStylingService.FONT_BOLD,
                        ExcelStylingService.ALIGN_CENTER_WRAP,
                        ExcelStylingService.BORDER_THIN,
                    ),
                    CellData(
                        "D",
                        self._current_row,
                        month_year,
                        ExcelStylingService.FONT_BOLD,
                        ExcelStylingService.ALIGN_CENTER_WRAP,
                        ExcelStylingService.BORDER_THIN,
                    ),
                    CellData(
                        "E",
                        self._current_row,
                        cumul_text,
                        ExcelStylingService.FONT_BOLD,
                        ExcelStylingService.ALIGN_CENTER_WRAP,
                        ExcelStylingService.BORDER_THIN,
                    ),
                ],
            ),
        )

        self._current_row += 1
        self._first_data_row = self._current_row

        self._add_first_table_data(sheet, query_results)

    def _add_first_table_data(
        self, sheet: Worksheet, query_results: Dict[str, pd.DataFrame]
    ) -> None:
        subprograms: List[str] = []
        if "subprograms" in query_results:
            subprograms = query_results["subprograms"]["subprogram"].tolist()

        data_dicts: Dict[str, Dict[str, int]] = self._create_data_dictionaries(
            query_results
        )

        rows: List[RowData] = []
        for i, subprogram in enumerate(subprograms):
            row_number = self._first_data_row + i
            rows.append(
                RowData(
                    number=row_number,
                    cells=[
                        CellData(
                            "A",
                            row_number,
                            subprogram,
                            border=ExcelStylingService.BORDER_THIN,
                        ),
                        CellData(
                            "B",
                            row_number,
                            data_dicts["livraisons_mois"].get(subprogram, 0),
                            border=ExcelStylingService.BORDER_THIN,
                        ),
                        CellData(
                            "C",
                            row_number,
                            data_dicts["livraisons_cumul"].get(subprogram, 0),
                            border=ExcelStylingService.BORDER_THIN,
                        ),
                        CellData(
                            "D",
                            row_number,
                            data_dicts["lancements_mois"].get(subprogram, 0),
                            border=ExcelStylingService.BORDER_THIN,
                        ),
                        CellData(
                            "E",
                            row_number,
                            data_dicts["lancements_cumul"].get(subprogram, 0),
                            border=ExcelStylingService.BORDER_THIN,
                        ),
                    ],
                )
            )
        if rows:
            ExcelStylingService.batch_style_rows(sheet, rows)

        self._current_row = self._first_data_row + len(subprograms)

        total_row: RowData = RowData(
            number=self._current_row,
            cells=[
                CellData(
                    "A",
                    self._current_row,
                    "Total",
                    ExcelStylingService.FONT_BOLD,
                    ExcelStylingService.ALIGN_CENTER,
                    ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "B",
                    self._current_row,
                    ExcelStylingService.create_sum_formula(
                        "B", self._first_data_row, self._current_row - 1
                    ),
                    ExcelStylingService.FONT_BOLD,
                    ExcelStylingService.ALIGN_CENTER,
                    ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "C",
                    self._current_row,
                    ExcelStylingService.create_sum_formula(
                        "C", self._first_data_row, self._current_row - 1
                    ),
                    ExcelStylingService.FONT_BOLD,
                    ExcelStylingService.ALIGN_CENTER,
                    ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "D",
                    self._current_row,
                    ExcelStylingService.create_sum_formula(
                        "D", self._first_data_row, self._current_row - 1
                    ),
                    ExcelStylingService.FONT_BOLD,
                    ExcelStylingService.ALIGN_CENTER,
                    ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "E",
                    self._current_row,
                    ExcelStylingService.create_sum_formula(
                        "E", self._first_data_row, self._current_row - 1
                    ),
                    ExcelStylingService.FONT_BOLD,
                    ExcelStylingService.ALIGN_CENTER,
                    ExcelStylingService.BORDER_THIN,
                ),
            ],
        )
        ExcelStylingService.style_row(sheet, total_row)

        self._current_row += 2

    def _create_data_dictionaries(
        self, query_results: Dict[str, pd.DataFrame]
    ) -> Dict[str, Dict[str, int]]:
        data_dicts: Dict[str, Dict[str, int]] = {
            "lancements_mois": {},
            "lancements_cumul": {},
            "livraisons_mois": {},
            "livraisons_cumul": {},
        }
        mappings: List[Tuple[str, str, str, str]] = [
            ("lancements_mois", "lancements_mois", "subprogram", "count"),
            ("lancements_cumul", "lancements_cumul_annee", "subprogram", "count"),
            ("livraisons_mois", "livraisons_mois", "subprogram", "count"),
            ("livraisons_cumul", "livraisons_cumul_annee", "subprogram", "count"),
        ]
        for dict_key, query_key, subprogram_column, count_column in mappings:
            if query_key in query_results:
                df: pd.DataFrame = query_results[query_key]
                data_dicts[dict_key] = dict(
                    zip(df[subprogram_column], df[count_column])
                )
        return data_dicts

    def _add_second_table_header(self, sheet: Worksheet) -> None:
        ExcelStylingService.merge_and_style_cell(
            sheet,
            MergeData(
                "A",
                "E",
                self._current_row,
                self._current_row,
                value="Situation des programmes (à renseigner par la BNH, ex-CNL)",
                font=ExcelStylingService.FONT_BOLD,
                alignment=ExcelStylingService.ALIGN_CENTER,
            ),
        )
        self._current_row += 1

        ExcelStylingService.merge_and_style_cell(
            sheet,
            MergeData(
                "A",
                "E",
                self._current_row,
                self._current_row,
                value=f"Arrêté le {self._report_context.reporting_date.strftime('%d/%m/%Y')}",
                font=ExcelStylingService.FONT_BOLD,
                alignment=ExcelStylingService.ALIGN_CENTER,
            ),
        )
        self._current_row += 2

    def _add_second_table(
        self, sheet: Worksheet, query_results: Dict[str, pd.DataFrame]
    ) -> None:
        headers: List[Tuple[str, str]] = [
            ("A", "Programme"),
            ("B", "Consistance\n(1)"),
            ("C", "Achevés\n(2)"),
            ("D", "En cours\n(3)"),
            ("E", "Non lancés\n(1) - (2) - (3)"),
        ]
        header_row: RowData = RowData(
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
                for col, title in headers
            ],
        )
        ExcelStylingService.style_row(sheet, header_row)

        self._current_row += 1
        self._add_second_table_data(sheet, query_results, self._current_row)

    def _add_second_table_data(
        self, sheet: Worksheet, query_results: Dict[str, pd.DataFrame], start_row: int
    ) -> None:
        subprograms_situation: List[Tuple[str, int]] = []
        if "subprograms_situation" in query_results:
            df_prog: pd.DataFrame = query_results["subprograms_situation"]
            subprograms_situation = list(
                zip(df_prog["subprogram"], df_prog["aid_count"])
            )

        data_dicts: Dict[str, Dict[str, int]] = self._create_situation_dictionaries(
            query_results
        )

        rows: List[RowData] = []
        for i, (subprogram, aid_count) in enumerate(subprograms_situation):
            row_number: int = self._current_row + i
            rows.append(
                RowData(
                    number=row_number,
                    cells=[
                        CellData(
                            "A",
                            row_number,
                            subprogram,
                            border=ExcelStylingService.BORDER_THIN,
                        ),
                        CellData(
                            "B",
                            row_number,
                            aid_count,
                            border=ExcelStylingService.BORDER_THIN,
                        ),
                        CellData(
                            "C",
                            row_number,
                            data_dicts["acheves"].get(subprogram, 0),
                            border=ExcelStylingService.BORDER_THIN,
                        ),
                        CellData(
                            "D",
                            row_number,
                            data_dicts["en_cours"].get(subprogram, 0),
                            border=ExcelStylingService.BORDER_THIN,
                        ),
                        CellData(
                            "E",
                            row_number,
                            f"=B{row_number}-(C{row_number}+D{row_number})",
                            border=ExcelStylingService.BORDER_THIN,
                        ),
                    ],
                )
            )
        if rows:
            ExcelStylingService.batch_style_rows(sheet, rows)

        self._current_row += len(subprograms_situation)

        end_row: int = (
            start_row + len(subprograms_situation) - 1
            if subprograms_situation
            else start_row
        )
        total_row: RowData = RowData(
            number=self._current_row,
            cells=[
                CellData(
                    "A",
                    self._current_row,
                    "Total général",
                    ExcelStylingService.FONT_BOLD,
                    ExcelStylingService.ALIGN_CENTER,
                    ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "B",
                    self._current_row,
                    ExcelStylingService.create_sum_formula("B", start_row, end_row),
                    ExcelStylingService.FONT_BOLD,
                    ExcelStylingService.ALIGN_CENTER,
                    ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "C",
                    self._current_row,
                    ExcelStylingService.create_sum_formula("C", start_row, end_row),
                    ExcelStylingService.FONT_BOLD,
                    ExcelStylingService.ALIGN_CENTER,
                    ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "D",
                    self._current_row,
                    ExcelStylingService.create_sum_formula("D", start_row, end_row),
                    ExcelStylingService.FONT_BOLD,
                    ExcelStylingService.ALIGN_CENTER,
                    ExcelStylingService.BORDER_THIN,
                ),
                CellData(
                    "E",
                    self._current_row,
                    ExcelStylingService.create_sum_formula("E", start_row, end_row),
                    ExcelStylingService.FONT_BOLD,
                    ExcelStylingService.ALIGN_CENTER,
                    ExcelStylingService.BORDER_THIN,
                ),
            ],
        )
        ExcelStylingService.style_row(sheet, total_row)
        self._current_row += 2

    def _create_situation_dictionaries(
        self, query_results: Dict[str, pd.DataFrame]
    ) -> Dict[str, Dict[str, int]]:
        data_dicts: Dict[str, Dict[Any, Any]] = {
            "acheves": {},
            "en_cours": {},
        }
        mappings: List[Tuple[str, str, str, str]] = [
            ("acheves", "acheves_derniere_tranche", "subprogram", "acheves"),
            ("en_cours", "en_cours_calculation", "subprogram", "en_cours"),
        ]
        for dict_key, query_key, subprogram_column, value_column in mappings:
            if query_key in query_results:
                df: pd.DataFrame = query_results[query_key]
                data_dicts[dict_key] = dict(
                    zip(df[subprogram_column], df[value_column])
                )
        return data_dicts

    def _add_footer(self, sheet: Worksheet) -> None:
        ExcelStylingService.batch_merge_and_style_cells(
            sheet,
            [
                MergeData(
                    "A",
                    "B",
                    self._current_row,
                    self._current_row,
                    value="Visa du directeur régional de la BNH (ex-CNL)",
                    font=ExcelStylingService.FONT_BOLD,
                    alignment=ExcelStylingService.ALIGN_LEFT,
                ),
                MergeData(
                    "D",
                    "E",
                    self._current_row,
                    self._current_row,
                    value="Visa du directeur du logement",
                    font=ExcelStylingService.FONT_BOLD,
                    alignment=ExcelStylingService.ALIGN_RIGHT,
                ),
            ],
        )

    def _finalize_formatting(self, sheet: Worksheet) -> None:
        column_widths: Dict[str, int] = {"A": 25, "B": 20, "C": 20, "D": 20, "E": 20}
        ExcelStylingService.batch_style_columns(
            sheet,
            [ColumnData(letter, width) for letter, width in column_widths.items()],
        )
        ExcelStylingService.set_page_layout(
            sheet, orientation="portrait", fit_to_width=True
        )
        ExcelStylingService.set_page_margins(
            sheet, left=0.25, right=0.25, top=0.5, bottom=0.5
        )
