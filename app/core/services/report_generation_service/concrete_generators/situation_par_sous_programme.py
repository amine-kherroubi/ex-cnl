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
from app.core.services.excel_styling_service import ExcelStylingService


class SituationParSousProgrammeGenerator(BaseGenerator):
    __slots__ = (
        "_current_row",
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
        self._totals: Dict[str, int] = {}
        self._data_start_row: int = 0
        self._data_end_row: int = 0

    def configure(self, **kwargs: Any) -> None:
        if kwargs:
            self._logger.debug(
                f"Ignoring unused configuration parameters: {list(kwargs.keys())}"
            )

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

    def _format_query_with_context(self, query_template: str) -> str:
        self._logger.debug("Formatting query template with report context")

        formatted_query: str = query_template.replace(
            "{year}", str(self._report_context.year)
        ).replace("{month}", str(self._report_context.month.number))

        self._logger.debug(
            f"Placeholders replaced with: month={self._report_context.month.number}, "
            f"year={self._report_context.year}"
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

        title: str = "Situation financière par sous-programme"

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
            "D",
            "E",
            self._current_row,
            self._current_row,
            value="Engagement par la BNH",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
            border=ExcelStylingService.BORDER_THIN,
        )

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "F",
            "G",
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
            "H",
            "O",
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
            "H",
            "K",
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
            "L",
            "O",
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
            "H",
            "J",
            self._current_row,
            self._current_row,
            value="Aides",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
            border=ExcelStylingService.BORDER_THIN,
        )

        ExcelStylingService.apply_style_to_cell(
            sheet,
            "K",
            self._current_row,
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
            border=ExcelStylingService.BORDER_THIN,
            value="Montant (4)",
        )

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "L",
            "N",
            self._current_row,
            self._current_row,
            value="Aides",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
            border=ExcelStylingService.BORDER_THIN,
        )

        ExcelStylingService.apply_style_to_cell(
            sheet,
            "O",
            self._current_row,
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
            border=ExcelStylingService.BORDER_THIN,
            value="Montant (5)",
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

        # Get all subprograms from the registry
        subprograms_df: pd.DataFrame = SubprogramRegistry.get_subprograms_dataframe()

        data_dicts: Dict[str, Dict[str, Tuple[int, ...]]] = (
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

        # Store the start row
        self._data_start_row = self._current_row

        for i, (_, row) in enumerate(subprograms_df.iterrows()):
            subprogram: str = row["subprogram"]
            current_row: int = self._current_row + i

            self._add_single_data_row(
                sheet, current_row, subprogram, data_dicts, totals
            )

        self._data_end_row = self._current_row + len(subprograms_df) - 1
        self._current_row += len(subprograms_df)

        self._totals = totals

        self._logger.info(f"Added {len(subprograms_df)} data rows successfully")

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

    def _add_single_data_row(
        self,
        sheet: Worksheet,
        row: int,
        subprogram: str,
        data_dicts: Dict[str, Dict[str, Tuple[int, ...]]],
        totals: Dict[str, int],
    ) -> None:
        # Get the display name for the subprogram
        try:
            subprogram_obj = SubprogramRegistry.get_subprogram_by_database_alias(
                subprogram
            )
            display_name = subprogram_obj.name
        except ValueError:
            display_name = subprogram

        basic_values: List[Tuple[str, Any]] = [
            ("A", display_name),
            ("B", "-"),
            ("C", "-"),
        ]

        if subprogram in data_dicts["aides_inscrites"]:
            aides_data = data_dicts["aides_inscrites"][subprogram]
            aides, montants = aides_data[0], aides_data[1]
            basic_values.extend(
                [
                    ("D", aides if aides > 0 else "-"),
                    ("E", montants if montants > 0 else "-"),
                ]
            )
            totals["aides_inscrites"] += aides
            totals["montants_inscrits"] += montants
        else:
            basic_values.extend([("D", "-"), ("E", "-")])

        basic_values.extend([("F", "-"), ("G", "-")])

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
            subprogram,
            data_dicts["cumul_precedent"],
            ["H", "I", "J", "K"],
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
            subprogram,
            data_dicts["annee_actuelle"],
            ["L", "M", "N", "O"],
            totals,
            [
                "annee_actuelle_t1",
                "annee_actuelle_t2",
                "annee_actuelle_t3",
                "annee_actuelle_montant",
            ],
        )

        cumul_total = self._calculate_cumul_total(subprogram, data_dicts)
        ExcelStylingService.apply_style_to_cell(
            sheet,
            "P",
            row,
            font=ExcelStylingService.FONT_NORMAL,
            alignment=ExcelStylingService.ALIGNMENT_CENTER,
            border=ExcelStylingService.BORDER_THIN,
            value=cumul_total if cumul_total > 0 else "-",
        )
        totals["cumul_total"] += cumul_total

        final_columns: List[Tuple[str, str]] = [("Q", "-"), ("R", "-")]
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
        key: str,
        data_dict: Dict[str, Tuple[int, ...]],
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
        key: str,
        data_dicts: Dict[str, Dict[str, Tuple[int, ...]]],
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
            ("B", "-"),
            ("C", "-"),
            ("D", self._totals.get("aides_inscrites", 0)),
            ("E", self._totals.get("montants_inscrits", 0)),
            ("F", "-"),
            ("G", "-"),
            ("H", self._totals.get("cumul_precedent_t1", 0)),
            ("I", self._totals.get("cumul_precedent_t2", 0)),
            ("J", self._totals.get("cumul_precedent_t3", 0)),
            ("K", self._totals.get("cumul_precedent_montant", 0)),
            ("L", self._totals.get("annee_actuelle_t1", 0)),
            ("M", self._totals.get("annee_actuelle_t2", 0)),
            ("N", self._totals.get("annee_actuelle_t3", 0)),
            ("O", self._totals.get("annee_actuelle_montant", 0)),
            ("P", self._totals.get("cumul_total", 0)),
            ("Q", "-"),
            ("R", "-"),
        ]

        ExcelStylingService.apply_data_row_styling(
            sheet,
            self._current_row,
            total_values,
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER,
            border=ExcelStylingService.BORDER_THIN,
        )

        ExcelStylingService.apply_style_to_cell(
            sheet,
            "A",
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
            "A": 25,  # Sous-programme
            "B": 8,  # Aides notifiées
            "C": 12,  # Montants notifiés
            "D": 8,  # Aides inscrites
            "E": 12,  # Montants inscrits
            "F": 8,  # Aides inscrites (2)
            "G": 12,  # Montants inscrits (3)
            "H": 6,  # T1 (prev)
            "I": 6,  # T2 (prev)
            "J": 6,  # T3 (prev)
            "K": 12,  # Montant (4)
            "L": 6,  # T1 (curr)
            "M": 6,  # T2 (curr)
            "N": 6,  # T3 (curr)
            "O": 12,  # Montant (5)
            "P": 12,  # Cumul
            "Q": 12,  # Solde
            "R": 12,  # Reste
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

        monetary_columns = ["E", "K", "O", "P", "Q"]

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
