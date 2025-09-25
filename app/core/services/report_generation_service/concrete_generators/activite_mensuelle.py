from __future__ import annotations

# Imports de la bibliothèque standard
from datetime import date
from typing import Any

# Imports tiers
import pandas as pd
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Alignment

# Imports de l'application locale
from app.core.domain.models.report_context import ReportContext
from app.core.domain.models.report_specification import ReportSpecification
from app.core.domain.predefined_objects.subprograms import get_subprograms_dataframe
from app.core.infrastructure.data.data_repository import DataRepository
from app.core.infrastructure.file_io.file_io_service import FileIOService
from app.core.services.report_generation_service.base_generator import BaseGenerator
from app.core.services.excel_styling_service import ExcelStylingService


class ActiviteMensuelleGenerator(BaseGenerator):
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

    def configure(self, **kwargs: Any) -> None:
        """Configure the generator with additional parameters.

        This generator doesn't need additional configuration,
        but overrides the method to avoid NotImplementedError.
        """
        if kwargs:
            self._logger.debug(
                f"Ignoring unused configuration parameters: {list(kwargs.keys())}"
            )

    def _create_predefined_tables(self) -> None:
        self._logger.debug("Creating reference tables")
        try:
            self._logger.debug(f"Creating reference table 'programs'")

            df: pd.DataFrame = get_subprograms_dataframe()
            self._data_repository.create_table_from_dataframe("programs", df)

            rows, cols = df.shape
            self._logger.info(
                f"Reference table 'programs' created: {rows} rows and {cols} columns"
            )
            self._logger.debug(f"Columns for 'programs': {list(df.columns)}")

        except Exception as error:
            self._logger.exception(
                f"Failed to create reference table 'programs': {error}"
            )
            raise

    def _format_query_with_context(self, query_template: str) -> str:
        self._logger.debug("Formatting query template with report context")

        formatted_query: str = query_template

        formatted_query = formatted_query.replace(
            "{month}", str(self._report_context.month.number)
        ).replace("{year}", str(self._report_context.year))

        self._logger.debug(
            f"Placeholders replaced with: month={self._report_context.month.number}, year={self._report_context.year}"
        )

        self._logger.debug("Query formatting completed")
        return formatted_query

    def _add_content(
        self, sheet: Worksheet, query_results: dict[str, pd.DataFrame]
    ) -> None:
        self._add_first_table_header(sheet)
        self._add_first_table(sheet, query_results)
        self._add_second_table_header(sheet)
        self._add_second_table(sheet, query_results)
        self._add_footer(sheet)

    def _add_first_table_header(self, sheet: Worksheet) -> None:
        self._logger.debug("Ajout de l'en-tête du report")

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "A",
            "E",
            self._current_row,
            self._current_row,
            value="Habitat rural",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER,
        )
        self._logger.debug("Titre principal ajouté : Habitat rural")

        self._current_row += 1

        wilaya_text = f"Wilaya de {self._report_context.wilaya.value}"
        sheet[f"A{self._current_row}"] = wilaya_text
        sheet[f"A{self._current_row}"].font = ExcelStylingService.FONT_BOLD
        self._logger.debug(f"Wilaya ajoutée : {wilaya_text}")

        self._current_row += 1

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "A",
            "E",
            self._current_row,
            self._current_row,
            value="Activité mensuelle par sous-programme (à renseigner par la BNH, ex-CNL)",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
        )
        self._logger.debug("Titre du report ajouté")

        self._current_row += 1

        month_text: str = (
            f"Mois de {self._report_context.month} {self._report_context.year}"
        )
        ExcelStylingService.merge_and_style_cells(
            sheet,
            "A",
            "E",
            self._current_row,
            self._current_row,
            value=month_text,
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER,
        )
        self._logger.debug(f"Mois et année ajoutés : {month_text}")

        self._logger.info("En-tête du report terminé avec succès")

        self._current_row += 2

    def _add_first_table(
        self, sheet: Worksheet, query_results: dict[str, pd.DataFrame]
    ) -> None:
        self._logger.debug("Ajout du tableau principal de données")
        self._logger.debug(
            f"Résultats de requêtes disponibles : {list(query_results.keys())}"
        )

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "A",
            "A",
            self._current_row,
            self._current_row + 2,
            value="Programme",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
            border=ExcelStylingService.BORDER_THIN,
        )

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "B",
            "E",
            self._current_row,
            self._current_row,
            value=(
                f"État d'exécution des tranches financières durant le mois de "
                f"{self._report_context.month} {self._report_context.year}"
            ),
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
            border=ExcelStylingService.BORDER_THIN,
        )

        self._logger.debug("Légende du tableau ajoutée")

        self._current_row += 1

        self._logger.debug(
            f"Ajout des en-têtes de colonnes à la ligne {self._current_row}"
        )
        ExcelStylingService.merge_and_style_cells(
            sheet,
            "B",
            "C",
            self._current_row,
            self._current_row,
            value="Livraisons (libération de la dernière tranche)",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
            border=ExcelStylingService.BORDER_THIN,
        )

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "D",
            "E",
            self._current_row,
            self._current_row,
            value="Lancements (libération de la première tranche)",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER_WRAP,
            border=ExcelStylingService.BORDER_THIN,
        )

        self._current_row += 1

        sub_headers: list[tuple[str, str]] = [
            (
                "B",
                f"{self._report_context.month.capitalize()} {self._report_context.year}",
            ),
            ("C", self._get_cumul_text()),
            (
                "D",
                f"{self._report_context.month.capitalize()} {self._report_context.year}",
            ),
            ("E", self._get_cumul_text()),
        ]

        for col, text in sub_headers:
            sheet[f"{col}{self._current_row}"] = text
            sheet[f"{col}{self._current_row}"].font = ExcelStylingService.FONT_BOLD
            sheet[f"{col}{self._current_row}"].alignment = (
                ExcelStylingService.ALIGNMENT_CENTER_WRAP
            )
            sheet[f"{col}{self._current_row}"].border = ExcelStylingService.BORDER_THIN

        self._logger.debug("Sous-en-têtes ajoutés avec les plages de dates")

        self._current_row += 1

        self._add_first_table_data(sheet, query_results)

    def _get_cumul_text(self) -> str:

        end_day: int = (
            self._report_context.month.last_day(self._report_context.year)
            if not self._report_context.month.is_current
            else date.today().day
        )
        return (
            f"Cumul du 1er janvier au {end_day} "
            f"{self._report_context.month} {self._report_context.year}"
        )

    def _add_first_table_data(
        self, sheet: Worksheet, query_results: dict[str, pd.DataFrame]
    ) -> None:

        self._logger.debug(
            f"Début des lignes de données à la ligne {self._current_row}"
        )

        subprograms: list[str] = []
        if "subprograms" in query_results:
            subprograms = query_results["subprograms"]["subprogram"].tolist()
            self._logger.info(
                f"Trouvé {len(subprograms)} sous-programmes : {subprograms}"
            )
        else:
            self._logger.warning("Aucun résultat de requête 'subprograms' trouvé")

        data_dicts: dict[str, dict[str, int]] = self._create_data_dictionaries(
            query_results
        )

        totals: dict[str, int] = {
            "livraisons_mois": sum(data_dicts["livraisons_mois"].values()),
            "livraisons_cumul": sum(data_dicts["livraisons_cumul"].values()),
            "lancements_mois": sum(data_dicts["lancements_mois"].values()),
            "lancements_cumul": sum(data_dicts["lancements_cumul"].values()),
        }

        for i, subprogram in enumerate(subprograms):
            row: int = self._current_row + i
            self._add_program_row(sheet, row, subprogram, data_dicts)

        self._current_row += len(subprograms)
        self._add_total_row(sheet, self._current_row, totals)

        self._logger.info(f"Premier tableau terminé avec {len(subprograms)} programs")

        self._current_row += 2

    def _create_data_dictionaries(
        self, query_results: dict[str, pd.DataFrame]
    ) -> dict[str, dict[str, int]]:

        self._logger.debug("Création des dictionnaires de recherche")

        data_dicts: dict[str, dict[str, int]] = {
            "lancements_mois": {},
            "lancements_cumul": {},
            "livraisons_mois": {},
            "livraisons_cumul": {},
        }

        mappings: list[tuple[str, str, str, str]] = [
            ("lancements_mois", "lancements_mois", "subprogram", "count"),
            ("lancements_cumul", "lancements_cumul_annee", "subprogram", "count"),
            ("livraisons_mois", "livraisons_mois", "subprogram", "count"),
            ("livraisons_cumul", "livraisons_cumul_annee", "subprogram", "count"),
        ]

        for dict_key, query_key, prog_col, count_col in mappings:
            if query_key in query_results:
                df = query_results[query_key]
                data_dicts[dict_key] = dict(zip(df[prog_col], df[count_col]))
                self._logger.debug(
                    f"Données {dict_key} : {len(data_dicts[dict_key])} sous-programmes"
                )

        return data_dicts

    def _add_program_row(
        self,
        sheet: Worksheet,
        row: int,
        subprogram: str,
        data_dicts: dict[str, dict[str, int]],
    ) -> None:

        values: list[tuple[str, Any]] = [
            ("A", subprogram),
            ("B", data_dicts["livraisons_mois"].get(subprogram, 0) or "-"),
            ("C", data_dicts["livraisons_cumul"].get(subprogram, 0) or "-"),
            ("D", data_dicts["lancements_mois"].get(subprogram, 0) or "-"),
            ("E", data_dicts["lancements_cumul"].get(subprogram, 0) or "-"),
        ]

        for col, value in values:
            cell = sheet[f"{col}{row}"]
            cell.value = value
            cell.font = ExcelStylingService.FONT_NORMAL
            cell.alignment = ExcelStylingService.ALIGNMENT_CENTER
            cell.border = ExcelStylingService.BORDER_THIN

    def _add_total_row(
        self, sheet: Worksheet, row: int, totals: dict[str, int]
    ) -> None:

        values: list[tuple[str, Any]] = [
            ("A", "Total"),
            ("B", totals["livraisons_mois"]),
            ("C", totals["livraisons_cumul"]),
            ("D", totals["lancements_mois"]),
            ("E", totals["lancements_cumul"]),
        ]

        for col, value in values:
            cell = sheet[f"{col}{row}"]
            cell.value = value
            cell.font = ExcelStylingService.FONT_BOLD
            cell.alignment = ExcelStylingService.ALIGNMENT_CENTER
            cell.border = ExcelStylingService.BORDER_THIN

    def _add_second_table_header(self, sheet: Worksheet) -> None:
        ExcelStylingService.merge_and_style_cells(
            sheet,
            "A",
            "E",
            self._current_row,
            self._current_row,
            value="Situation des programs (à renseigner par la BNH, ex-CNL)",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER,
        )

        self._current_row += 1

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "A",
            "E",
            self._current_row,
            self._current_row,
            value=f"Arrêté le {self._report_context.reporting_date.strftime('%d/%m/%Y')}",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_CENTER,
        )

        self._current_row += 2

    def _add_second_table(
        self, sheet: Worksheet, query_results: dict[str, pd.DataFrame]
    ) -> None:
        self._logger.debug("Ajout du second tableau (SITUATION DES PROGRAMMES)")

        headers: list[tuple[str, str]] = [
            ("A", "Programme"),
            ("B", "Consistance"),
            ("C", "Achevés (dernières tranches payées)"),
            ("D", "En cours"),
            ("E", "Non lancés (consistance - premières tranches payées)"),
        ]

        for col, title in headers:
            cell = sheet[f"{col}{self._current_row}"]
            cell.value = title
            cell.font = ExcelStylingService.FONT_BOLD
            cell.alignment = ExcelStylingService.ALIGNMENT_CENTER_WRAP
            cell.border = ExcelStylingService.BORDER_THIN

        self._current_row += 1

        self._add_second_table_data(sheet, query_results)

    def _add_second_table_data(
        self, sheet: Worksheet, query_results: dict[str, pd.DataFrame]
    ) -> None:

        subprograms_situation: list[tuple[str, int]] = []
        if "subprograms_situation" in query_results:
            df_prog = query_results["subprograms_situation"]
            subprograms_situation = list(
                zip(df_prog["subprogram"], df_prog["aid_count"])
            )
            self._logger.info(
                f"Trouvé {len(subprograms_situation)} sous-programmes pour le tableau de situation"
            )

        data_dicts = self._create_situation_dictionaries(query_results)

        totals = {"aid_count": 0, "finished": 0, "current": 0, "not_started": 0}

        for i, (subprogram, aid_count) in enumerate(subprograms_situation):
            row = self._current_row + i
            self._add_situation_row(
                sheet, row, subprogram, aid_count, data_dicts, totals
            )

        self._current_row += len(subprograms_situation)
        self._add_situation_total_row(sheet, self._current_row, totals)

        self._logger.info(
            f"Second tableau terminé avec {len(subprograms_situation)} sous-programmes"
        )
        self._current_row += 2

    def _create_situation_dictionaries(
        self, query_results: dict[str, pd.DataFrame]
    ) -> dict[str, dict[str, int]]:

        data_dicts: dict[str, dict[str, int]] = {
            "acheves": {},
            "en_cours": {},
            "non_lances": {},
        }

        mappings: list[tuple[str, str, str, str]] = [
            ("acheves", "acheves_derniere_tranche", "subprogram", "acheves"),
            ("en_cours", "en_cours_calculation", "subprogram", "en_cours"),
            ("non_lances", "non_lances_premiere_tranche", "subprogram", "non_lances"),
        ]

        for dict_key, query_key, prog_col, value_col in mappings:
            if query_key in query_results:
                df = query_results[query_key]
                data_dicts[dict_key] = dict(zip(df[prog_col], df[value_col]))

        return data_dicts

    def _add_situation_row(
        self,
        sheet: Worksheet,
        row: int,
        subprogram: str,
        aid_count: int,
        data_dicts: dict[str, dict[str, int]],
        totals: dict[str, int],
    ) -> None:

        finished: int = data_dicts["acheves"].get(subprogram, 0)
        current: int = data_dicts["en_cours"].get(subprogram, 0)
        not_started: int = data_dicts["non_lances"].get(subprogram, 0)

        values: list[tuple[str, Any]] = [
            ("A", subprogram),
            ("B", aid_count),
            ("C", finished if finished > 0 else "-"),
            ("D", current if current > 0 else "-"),
            ("E", not_started if not_started > 0 else "-"),
        ]

        for col, value in values:
            cell = sheet[f"{col}{row}"]
            cell.value = value
            cell.font = ExcelStylingService.FONT_NORMAL
            cell.alignment = ExcelStylingService.ALIGNMENT_CENTER
            cell.border = ExcelStylingService.BORDER_THIN

        totals["aid_count"] += aid_count
        totals["finished"] += finished
        totals["current"] += current
        totals["not_started"] += not_started

    def _add_situation_total_row(
        self, sheet: Worksheet, row: int, totals: dict[str, int]
    ) -> None:

        values: list[tuple[str, Any]] = [
            ("A", "Total général"),
            ("B", totals["aid_count"]),
            ("C", totals["finished"]),
            ("D", totals["current"]),
            ("E", totals["not_started"]),
        ]

        for col, value in values:
            cell = sheet[f"{col}{row}"]
            cell.value = value
            cell.font = ExcelStylingService.FONT_BOLD
            cell.alignment = ExcelStylingService.ALIGNMENT_CENTER
            cell.border = ExcelStylingService.BORDER_THIN

    def _add_footer(self, sheet: Worksheet) -> None:
        self._logger.debug("Ajout du pied de page du report")

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "A",
            "B",
            self._current_row,
            self._current_row,
            value="Visa du directeur régional de la BNH (ex-CNL)",
            font=ExcelStylingService.FONT_BOLD,
            alignment=ExcelStylingService.ALIGNMENT_LEFT,
        )

        ExcelStylingService.merge_and_style_cells(
            sheet,
            "D",
            "E",
            self._current_row,
            self._current_row,
            value="Visa du directeur du logement",
            font=ExcelStylingService.FONT_BOLD,
            alignment=Alignment(horizontal="right", vertical="center"),
        )

        self._logger.debug("Pied de page ajouté avec succès")

    def _finalize_formatting(self, sheet: Worksheet) -> None:

        self._logger.debug("Applying final formatting")

        column_widths: dict[str, int] = {
            "A": 25,
            "B": 18,
            "C": 22,
            "D": 18,
            "E": 22,
        }

        ExcelStylingService.set_column_widths(sheet, column_widths)

        ExcelStylingService.setup_page_layout(
            sheet,
            orientation="portrait",
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
