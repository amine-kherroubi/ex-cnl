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
from app.core.domain.predefined_objects.programmes import get_programmes_dataframe
from app.core.infrastructure.data.data_repository import DataRepository
from app.core.infrastructure.file_io.file_io_service import FileIOService
from app.core.services.report_generation.base.report_generator import ReportGenerator
from app.core.utils.excel_styling import ExcelStyling


class ActiviteMensuelleGenerator(ReportGenerator):
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

        # Titre
        ExcelStyling.merge_and_style_cells(
            sheet,
            "A",
            "E",
            self._current_row,
            self._current_row,
            value="Habitat rural",
            font=ExcelStyling.FONT_BOLD,
            alignment=ExcelStyling.ALIGNMENT_CENTER,
        )
        self._logger.debug("Titre principal ajouté : Habitat rural")

        self._current_row += 1

        # Wilaya
        wilaya_text = f"Wilaya de {self._report_context.wilaya.value}"
        sheet[f"A{self._current_row}"] = wilaya_text
        sheet[f"A{self._current_row}"].font = ExcelStyling.FONT_BOLD
        self._logger.debug(f"Wilaya ajoutée : {wilaya_text}")

        self._current_row += 1

        # Titre principal
        ExcelStyling.merge_and_style_cells(
            sheet,
            "A",
            "E",
            self._current_row,
            self._current_row,
            value="Activité mensuelle par programme (à renseigner par la BNH, ex-CNL)",
            font=ExcelStyling.FONT_BOLD,
            alignment=ExcelStyling.ALIGNMENT_CENTER_WRAP,
        )
        self._logger.debug("Titre du report ajouté")

        self._current_row += 1

        # Mois
        month_text: str = (
            f"Mois de {self._report_context.month} {self._report_context.year}"
        )
        ExcelStyling.merge_and_style_cells(
            sheet,
            "A",
            "E",
            self._current_row,
            self._current_row,
            value=month_text,
            font=ExcelStyling.FONT_BOLD,
            alignment=ExcelStyling.ALIGNMENT_CENTER,
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

        # La cellule Programme s'étend sur 3 lignes
        ExcelStyling.merge_and_style_cells(
            sheet,
            "A",
            "A",
            self._current_row,
            self._current_row + 2,
            value="Programme",
            font=ExcelStyling.FONT_BOLD,
            alignment=ExcelStyling.ALIGNMENT_CENTER_WRAP,
            border=ExcelStyling.BORDER_THIN,
        )

        ExcelStyling.merge_and_style_cells(
            sheet,
            "B",
            "E",
            self._current_row,
            self._current_row,
            value=(
                f"État d'exécution des tranches financières durant le mois de "
                f"{self._report_context.month} {self._report_context.year}"
            ),
            font=ExcelStyling.FONT_BOLD,
            alignment=ExcelStyling.ALIGNMENT_CENTER_WRAP,
            border=ExcelStyling.BORDER_THIN,
        )

        self._logger.debug("Légende du tableau ajoutée")

        self._current_row += 1

        # En-têtes
        self._logger.debug(
            f"Ajout des en-têtes de colonnes à la ligne {self._current_row}"
        )
        ExcelStyling.merge_and_style_cells(
            sheet,
            "B",
            "C",
            self._current_row,
            self._current_row,
            value="Livraisons (libération de la dernière tranche)",
            font=ExcelStyling.FONT_BOLD,
            alignment=ExcelStyling.ALIGNMENT_CENTER_WRAP,
            border=ExcelStyling.BORDER_THIN,
        )

        ExcelStyling.merge_and_style_cells(
            sheet,
            "D",
            "E",
            self._current_row,
            self._current_row,
            value="Lancements (libération de la première tranche)",
            font=ExcelStyling.FONT_BOLD,
            alignment=ExcelStyling.ALIGNMENT_CENTER_WRAP,
            border=ExcelStyling.BORDER_THIN,
        )

        self._current_row += 1

        # Sous-en-têtes
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
            sheet[f"{col}{self._current_row}"].font = ExcelStyling.FONT_BOLD
            sheet[f"{col}{self._current_row}"].alignment = (
                ExcelStyling.ALIGNMENT_CENTER_WRAP
            )
            sheet[f"{col}{self._current_row}"].border = ExcelStyling.BORDER_THIN

        self._logger.debug("Sous-en-têtes ajoutés avec les plages de dates")

        self._current_row += 1

        # Ajouter les données des résultats de requêtes
        self._add_first_table_data(sheet, query_results)

    def _get_cumul_text(self) -> str:
        """Generate the cumulative text based on the current month."""
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
        """Add data rows to the first table."""
        self._logger.debug(
            f"Début des lignes de données à la ligne {self._current_row}"
        )

        # Obtenir tous les programmes
        programmes: list[str] = []
        if "programmes" in query_results:
            programmes = query_results["programmes"]["programme"].tolist()
            self._logger.info(f"Trouvé {len(programmes)} programmes : {programmes}")
        else:
            self._logger.warning("Aucun résultat de requête 'programmes' trouvé")

        # Créer des dictionnaires de recherche
        data_dicts: dict[str, dict[str, int]] = self._create_data_dictionaries(
            query_results
        )

        # Calculer les totaux
        totals: dict[str, int] = {
            "livraisons_mois": sum(data_dicts["livraisons_mois"].values()),
            "livraisons_cumul": sum(data_dicts["livraisons_cumul"].values()),
            "lancements_mois": sum(data_dicts["lancements_mois"].values()),
            "lancements_cumul": sum(data_dicts["lancements_cumul"].values()),
        }

        # Ajouter les lignes de données
        for i, programme in enumerate(programmes):
            row: int = self._current_row + i
            self._add_programme_row(sheet, row, programme, data_dicts)

        # Ajouter la ligne Total
        self._current_row += len(programmes)
        self._add_total_row(sheet, self._current_row, totals)

        self._logger.info(f"Premier tableau terminé avec {len(programmes)} programmes")

        self._current_row += 2

    def _create_data_dictionaries(
        self, query_results: dict[str, pd.DataFrame]
    ) -> dict[str, dict[str, int]]:
        """Create lookup dictionaries from query results."""
        self._logger.debug("Création des dictionnaires de recherche")

        data_dicts: dict[str, dict[str, int]] = {
            "lancements_mois": {},
            "lancements_cumul": {},
            "livraisons_mois": {},
            "livraisons_cumul": {},
        }

        mappings = [
            ("lancements_mois", "lancements_mois", "programme", "count"),
            ("lancements_cumul", "lancements_cumul_annee", "programme", "count"),
            ("livraisons_mois", "livraisons_mois", "programme", "count"),
            ("livraisons_cumul", "livraisons_cumul_annee", "programme", "count"),
        ]

        for dict_key, query_key, prog_col, count_col in mappings:
            if query_key in query_results:
                df = query_results[query_key]
                data_dicts[dict_key] = dict(zip(df[prog_col], df[count_col]))
                self._logger.debug(
                    f"Données {dict_key} : {len(data_dicts[dict_key])} programmes"
                )

        return data_dicts

    def _add_programme_row(
        self,
        sheet: Worksheet,
        row: int,
        programme: str,
        data_dicts: dict[str, dict[str, int]],
    ) -> None:
        """Add a single programme row to the table."""
        values: list[tuple[str, Any]] = [
            ("A", programme),
            ("B", data_dicts["livraisons_mois"].get(programme, 0) or "-"),
            ("C", data_dicts["livraisons_cumul"].get(programme, 0) or "-"),
            ("D", data_dicts["lancements_mois"].get(programme, 0) or "-"),
            ("E", data_dicts["lancements_cumul"].get(programme, 0) or "-"),
        ]

        for col, value in values:
            cell = sheet[f"{col}{row}"]
            cell.value = value
            cell.font = ExcelStyling.FONT_NORMAL
            cell.alignment = ExcelStyling.ALIGNMENT_CENTER
            cell.border = ExcelStyling.BORDER_THIN

    def _add_total_row(
        self, sheet: Worksheet, row: int, totals: dict[str, int]
    ) -> None:
        """Add a total row to the table."""
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
            cell.font = ExcelStyling.FONT_BOLD
            cell.alignment = ExcelStyling.ALIGNMENT_CENTER
            cell.border = ExcelStyling.BORDER_THIN

    def _add_second_table_header(self, sheet: Worksheet) -> None:
        ExcelStyling.merge_and_style_cells(
            sheet,
            "A",
            "E",
            self._current_row,
            self._current_row,
            value="Situation des programmes (à renseigner par la BNH, ex-CNL)",
            font=ExcelStyling.FONT_BOLD,
            alignment=ExcelStyling.ALIGNMENT_CENTER,
        )

        self._current_row += 1

        ExcelStyling.merge_and_style_cells(
            sheet,
            "A",
            "E",
            self._current_row,
            self._current_row,
            value=f"Arrêté le {self._report_context.reporting_date.strftime('%d/%m/%Y')}",
            font=ExcelStyling.FONT_BOLD,
            alignment=ExcelStyling.ALIGNMENT_CENTER,
        )

        self._current_row += 2

    def _add_second_table(
        self, sheet: Worksheet, query_results: dict[str, pd.DataFrame]
    ) -> None:
        self._logger.debug("Ajout du second tableau (SITUATION DES PROGRAMMES)")

        # En-têtes du second tableau
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
            cell.font = ExcelStyling.FONT_BOLD
            cell.alignment = ExcelStyling.ALIGNMENT_CENTER_WRAP
            cell.border = ExcelStyling.BORDER_THIN

        self._current_row += 1

        # Add second table data
        self._add_second_table_data(sheet, query_results)

    def _add_second_table_data(
        self, sheet: Worksheet, query_results: dict[str, pd.DataFrame]
    ) -> None:
        """Add data rows to the second table."""
        # Get programmes data
        programmes_situation: list[tuple[str, int]] = []
        if "programmes_situation" in query_results:
            df_prog = query_results["programmes_situation"]
            programmes_situation = list(
                zip(df_prog["programme"], df_prog["consistance"])
            )
            self._logger.info(
                f"Trouvé {len(programmes_situation)} programmes pour le tableau de situation"
            )

        # Create lookup dictionaries
        data_dicts = self._create_situation_dictionaries(query_results)

        # Initialize totals
        totals = {"consistance": 0, "acheves": 0, "en_cours": 0, "non_lances": 0}

        # Add data rows
        for i, (programme, consistance) in enumerate(programmes_situation):
            row = self._current_row + i
            self._add_situation_row(
                sheet, row, programme, consistance, data_dicts, totals
            )

        # Add total row
        self._current_row += len(programmes_situation)
        self._add_situation_total_row(sheet, self._current_row, totals)

        self._logger.info(
            f"Second tableau terminé avec {len(programmes_situation)} programmes"
        )
        self._current_row += 2

    def _create_situation_dictionaries(
        self, query_results: dict[str, pd.DataFrame]
    ) -> dict[str, dict[str, int]]:
        """Create lookup dictionaries for situation table."""
        data_dicts: dict[str, dict[str, int]] = {
            "acheves": {},
            "en_cours": {},
            "non_lances": {},
        }

        mappings = [
            ("acheves", "acheves_derniere_tranche", "programme", "acheves"),
            ("en_cours", "en_cours_calculation", "programme", "en_cours"),
            ("non_lances", "non_lances_premiere_tranche", "programme", "non_lances"),
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
        programme: str,
        consistance: int,
        data_dicts: dict[str, dict[str, int]],
        totals: dict[str, int],
    ) -> None:
        """Add a single situation row."""
        acheves = data_dicts["acheves"].get(programme, 0)
        en_cours = data_dicts["en_cours"].get(programme, 0)
        non_lances = data_dicts["non_lances"].get(programme, 0)

        values: list[tuple[str, Any]] = [
            ("A", programme),
            ("B", consistance),
            ("C", acheves if acheves > 0 else "-"),
            ("D", en_cours if en_cours > 0 else "-"),
            ("E", non_lances if non_lances > 0 else "-"),
        ]

        for col, value in values:
            cell = sheet[f"{col}{row}"]
            cell.value = value
            cell.font = ExcelStyling.FONT_NORMAL
            cell.alignment = ExcelStyling.ALIGNMENT_CENTER
            cell.border = ExcelStyling.BORDER_THIN

        # Update totals
        totals["consistance"] += consistance
        totals["acheves"] += acheves
        totals["en_cours"] += en_cours
        totals["non_lances"] += non_lances

    def _add_situation_total_row(
        self, sheet: Worksheet, row: int, totals: dict[str, int]
    ) -> None:
        """Add total row for situation table."""
        values: list[tuple[str, Any]] = [
            ("A", "Total général"),
            ("B", totals["consistance"]),
            ("C", totals["acheves"]),
            ("D", totals["en_cours"]),
            ("E", totals["non_lances"]),
        ]

        for col, value in values:
            cell = sheet[f"{col}{row}"]
            cell.value = value
            cell.font = ExcelStyling.FONT_BOLD
            cell.alignment = ExcelStyling.ALIGNMENT_CENTER
            cell.border = ExcelStyling.BORDER_THIN

    def _add_footer(self, sheet: Worksheet) -> None:
        self._logger.debug("Ajout du pied de page du report")

        # Texte de pied de page gauche (A-B)
        ExcelStyling.merge_and_style_cells(
            sheet,
            "A",
            "B",
            self._current_row,
            self._current_row,
            value="Visa du directeur régional de la BNH (ex-CNL)",
            font=ExcelStyling.FONT_BOLD,
            alignment=ExcelStyling.ALIGNMENT_LEFT,
        )

        # Texte de pied de page droit (D-E)
        ExcelStyling.merge_and_style_cells(
            sheet,
            "D",
            "E",
            self._current_row,
            self._current_row,
            value="Visa du directeur du logement",
            font=ExcelStyling.FONT_BOLD,
            alignment=Alignment(horizontal="right", vertical="center"),
        )

        self._logger.debug("Pied de page ajouté avec succès")

    def _finalize_formatting(self, sheet: Worksheet) -> None:
        """Apply final formatting to the worksheet."""
        self._logger.debug("Applying final formatting")

        column_widths: dict[str, int] = {
            "A": 25,
            "B": 18,
            "C": 22,
            "D": 18,
            "E": 22,
        }

        ExcelStyling.set_column_widths(sheet, column_widths)

        ExcelStyling.setup_page_layout(
            sheet,
            orientation="portrait",
            fit_to_width=True,
            fit_to_height=False,
        )

        ExcelStyling.setup_page_margins(
            sheet,
            left=0.25,
            right=0.25,
            top=0.5,
            bottom=0.5,
        )

        self._logger.info("Final formatting completed successfully")
