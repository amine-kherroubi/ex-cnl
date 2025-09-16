from __future__ import annotations

# Imports de la bibliothèque standard
from typing import Any

# Imports tiers
import pandas as pd
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Alignment, Border, Font, Side, PatternFill

# Imports de l'application locale
from app.core.domain.models.report_context import ReportContext
from app.core.domain.models.report_specification import ReportSpecification
from app.core.infrastructure.data.data_repository import DataRepository
from app.core.infrastructure.file_io.file_io_service import FileIOService
from app.core.services.report_generation.base.report_generator import ReportGenerator


class SituationFinanciereGenerator(ReportGenerator):
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

    def _add_content(
        self, sheet: Worksheet, query_results: dict[str, pd.DataFrame]
    ) -> None:
        self._add_header(sheet)
        self._add_table_headers(sheet)
        self._add_data_rows(sheet, query_results)
        self._add_totals_row(sheet, query_results)

    def _add_header(self, sheet: Worksheet) -> None:
        self._logger.debug("Ajout de l'en-tête du rapport")

        # Numéro de tableau
        sheet[f"O{self._current_row}"] = "TABLEAU 01"
        sheet[f"O{self._current_row}"].font = Font(name="Arial", size=10, bold=True)
        sheet[f"O{self._current_row}"].alignment = Alignment(horizontal="right")

        self._current_row += 1

        # Titre principal
        sheet[f"A{self._current_row}"] = (
            "SITUATION FINANCIÈRE DES PROGRAMMES DE LOGEMENTS AIDÉS PAR PROGRAMME, DAIRA ET PAR COMMUNE"
        )
        sheet.merge_cells(f"A{self._current_row}:O{self._current_row}")
        sheet[f"A{self._current_row}"].font = Font(name="Arial", size=11, bold=True)
        sheet[f"A{self._current_row}"].alignment = Alignment(
            horizontal="center", vertical="center"
        )

        self._current_row += 1

        # Programme
        programme_name: str = (
            self._report_context.programme
            if hasattr(self._report_context, "programme")
            else "PROGRAMME DE LOGEMENTS AIDÉS EN MILIEU RURAL"
        )
        sheet[f"A{self._current_row}"] = programme_name
        sheet.merge_cells(f"A{self._current_row}:O{self._current_row}")
        sheet[f"A{self._current_row}"].font = Font(name="Arial", size=10, bold=True)
        sheet[f"A{self._current_row}"].alignment = Alignment(
            horizontal="center", vertical="center"
        )

        self._current_row += 1

        # Date d'arrêté
        sheet[f"A{self._current_row}"] = (
            f"ARRÊTÉ AU {self._report_context.report_date.strftime('%d/%m/%Y')}"
        )
        sheet.merge_cells(f"A{self._current_row}:O{self._current_row}")
        sheet[f"A{self._current_row}"].font = Font(name="Arial", size=10, bold=True)
        sheet[f"A{self._current_row}"].alignment = Alignment(
            horizontal="center", vertical="center"
        )

        self._current_row += 1

        # DL de wilaya
        sheet[f"A{self._current_row}"] = (
            f"DL DE {self._report_context.wilaya.value.upper()}"
        )
        sheet[f"A{self._current_row}"].font = Font(name="Arial", size=10, bold=True)

        self._current_row += 2

    def _add_table_headers(self, sheet: Worksheet) -> None:
        self._logger.debug("Ajout des en-têtes de colonnes")

        # Structure des en-têtes multi-niveaux
        start_row: int = self._current_row

        # Première ligne d'en-têtes
        sheet[f"A{start_row}"] = "DAIRA"
        sheet.merge_cells(f"A{start_row}:A{start_row + 2}")

        sheet[f"B{start_row}"] = "COMMUNES"
        sheet.merge_cells(f"B{start_row}:B{start_row + 2}")

        sheet[f"C{start_row}"] = "NOMBRE TOTAL D'AIDES INSCRITS"
        sheet.merge_cells(f"C{start_row}:C{start_row + 2}")

        sheet[f"D{start_row}"] = "ENGAGEMENT PAR BNH (EX CNL)"
        sheet.merge_cells(f"D{start_row}:G{start_row}")

        sheet[f"H{start_row}"] = "ENGAGEMENT PAR MDV (DÉCISION D'INSCRIPTION)"
        sheet.merge_cells(f"H{start_row}:I{start_row}")

        sheet[f"J{start_row}"] = "CONSOMMATIONS"
        sheet.merge_cells(f"J{start_row}:M{start_row}")

        sheet[f"N{start_row}"] = "% CONSOMMÉ"
        sheet.merge_cells(f"N{start_row}:N{start_row + 2}")

        sheet[f"O{start_row}"] = "SOLDE MONTANT (Reste à payer)"
        sheet.merge_cells(f"O{start_row}:O{start_row + 2}")

        sheet[f"P{start_row}"] = "RESTE NOMBRE (Fin de chantier)"
        sheet.merge_cells(f"P{start_row}:P{start_row + 2}")

        # Deuxième ligne d'en-têtes
        second_row: int = start_row + 1

        sheet[f"D{second_row}"] = "NOMBRE D'AIDES INSCRITS"
        sheet[f"E{second_row}"] = "MONTANTS INSCRITS"
        sheet[f"F{second_row}"] = "NOMBRE D'AIDES LANCÉS (1ère tranche)"
        sheet[f"G{second_row}"] = "MONTANTS DÉCRITS (5)"

        sheet[f"H{second_row}"] = "NOMBRE D'AIDES"
        sheet[f"I{second_row}"] = "MONTANTS"

        sheet[f"J{second_row}"] = "CUMULES AU 31/12/2024"
        sheet.merge_cells(f"J{second_row}:K{second_row}")

        sheet[f"L{second_row}"] = (
            f"DE JANVIER 2025 À {self._report_context.month.value.upper() if self._report_context.month else 'MARS'} 2025"
        )
        sheet.merge_cells(f"L{second_row}:M{second_row}")

        # Troisième ligne d'en-têtes
        third_row: int = start_row + 2

        sheet[f"D{third_row}"] = ""
        sheet[f"E{third_row}"] = ""
        sheet[f"F{third_row}"] = ""
        sheet[f"G{third_row}"] = ""
        sheet[f"H{third_row}"] = ""
        sheet[f"I{third_row}"] = ""

        sheet[f"J{third_row}"] = "NOMBRE D'AIDES"
        sheet[f"K{third_row}"] = "MONTANT (4)"
        sheet[f"L{third_row}"] = "NOMBRE D'AIDES"
        sheet[f"M{third_row}"] = "MONTANT (5)"

        # Appliquer le formatage aux en-têtes
        for row in range(start_row, start_row + 3):
            for col in [
                "A",
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
            ]:
                cell = sheet[f"{col}{row}"]
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

        # Numérotation des colonnes
        self._current_row = start_row + 3
        sheet[f"J{self._current_row}"] = "T1"
        sheet[f"K{self._current_row}"] = "T2"
        sheet[f"L{self._current_row}"] = "T3"
        sheet[f"M{self._current_row}"] = ""

        for col in ["J", "K", "L", "M"]:
            cell = sheet[f"{col}{self._current_row}"]
            cell.font = Font(name="Arial", size=8)
            cell.alignment = Alignment(horizontal="center")

        self._current_row += 1

    def _add_data_rows(
        self, sheet: Worksheet, query_results: dict[str, pd.DataFrame]
    ) -> None:
        self._logger.debug("Ajout des lignes de données")

        # Récupérer les données de base
        data_by_daira_commune = query_results.get(
            "data_by_daira_commune", pd.DataFrame()
        )

        if data_by_daira_commune.empty:
            self._logger.warning("Aucune donnée trouvée pour daira/commune")
            return

        # Grouper les données par daira
        daira_groups = data_by_daira_commune.groupby("daira", sort=False)

        for daira, communes_data in daira_groups:
            daira_start_row = self._current_row
            communes_count = len(communes_data)

            # Ajouter le nom de la daira (fusionner les cellules si plusieurs communes)
            sheet[f"A{daira_start_row}"] = daira
            if communes_count > 1:
                sheet.merge_cells(
                    f"A{daira_start_row}:A{daira_start_row + communes_count - 1}"
                )

            # Ajouter les données pour chaque commune
            for idx, (_, row) in enumerate(communes_data.iterrows()):
                row_num = daira_start_row + idx

                # Commune
                sheet[f"B{row_num}"] = row.get("commune", "")

                # Nombre total d'aides inscrits
                sheet[f"C{row_num}"] = row.get("nb_aides_inscrits", 0)

                # Engagement par BNH
                sheet[f"D{row_num}"] = row.get("nb_aides_bnh", 0)
                sheet[f"E{row_num}"] = row.get("montants_inscrits", 0)
                sheet[f"F{row_num}"] = row.get("nb_aides_lances", 0)
                sheet[f"G{row_num}"] = row.get("montants_decrits", 0)

                # Engagement par MDV
                sheet[f"H{row_num}"] = row.get("nb_aides_mdv", 0)
                sheet[f"I{row_num}"] = row.get("montants_mdv", 0)

                # Consommations
                sheet[f"J{row_num}"] = row.get("nb_aides_cumul_2024", 0)
                sheet[f"K{row_num}"] = f'{row.get("montant_cumul_2024", 0):,.0f}'
                sheet[f"L{row_num}"] = row.get("nb_aides_2025", 0)
                sheet[f"M{row_num}"] = f'{row.get("montant_2025", 0):,.0f}'

                # % Consommé
                total_montant = row.get("montants_inscrits", 0)
                montant_consomme = row.get("montant_cumul_2024", 0) + row.get(
                    "montant_2025", 0
                )
                pourcentage = (
                    (montant_consomme / total_montant * 100) if total_montant > 0 else 0
                )
                sheet[f"N{row_num}"] = f"{pourcentage:.1f}%"

                # Solde
                sheet[f"O{row_num}"] = f"{total_montant - montant_consomme:,.0f}"

                # Reste nombre
                sheet[f"P{row_num}"] = (
                    row.get("nb_aides_inscrits", 0)
                    - row.get("nb_aides_cumul_2024", 0)
                    - row.get("nb_aides_2025", 0)
                )

                # Appliquer le formatage
                for col in [
                    "A",
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
                ]:
                    cell = sheet[f"{col}{row_num}"]
                    cell.font = Font(name="Arial", size=9)
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.border = Border(
                        left=Side(style="thin"),
                        right=Side(style="thin"),
                        top=Side(style="thin"),
                        bottom=Side(style="thin"),
                    )

            self._current_row += communes_count

    def _add_totals_row(
        self, sheet: Worksheet, query_results: dict[str, pd.DataFrame]
    ) -> None:
        self._logger.debug("Ajout de la ligne des totaux")

        # Récupérer les totaux depuis les résultats de requêtes
        totals = query_results.get("totals", pd.DataFrame())

        if totals.empty:
            self._logger.warning("Aucune donnée de totaux trouvée")
            return

        total_row = totals.iloc[0] if not totals.empty else {}

        # Ajouter la ligne de totaux
        sheet[f"A{self._current_row}"] = "TOTAL"
        sheet.merge_cells(f"A{self._current_row}:B{self._current_row}")

        # Remplir les totaux
        sheet[f"C{self._current_row}"] = total_row.get("total_aides_inscrits", 0)
        sheet[f"D{self._current_row}"] = total_row.get("total_aides_bnh", 0)
        sheet[f"E{self._current_row}"] = (
            f'{total_row.get("total_montants_inscrits", 0):,.0f}'
        )
        sheet[f"F{self._current_row}"] = total_row.get("total_aides_lances", 0)
        sheet[f"G{self._current_row}"] = (
            f'{total_row.get("total_montants_decrits", 0):,.0f}'
        )
        sheet[f"H{self._current_row}"] = total_row.get("total_aides_mdv", 0)
        sheet[f"I{self._current_row}"] = (
            f'{total_row.get("total_montants_mdv", 0):,.0f}'
        )
        sheet[f"J{self._current_row}"] = total_row.get("total_aides_cumul_2024", 0)
        sheet[f"K{self._current_row}"] = (
            f'{total_row.get("total_montant_cumul_2024", 0):,.0f}'
        )
        sheet[f"L{self._current_row}"] = total_row.get("total_aides_2025", 0)
        sheet[f"M{self._current_row}"] = (
            f'{total_row.get("total_montant_2025", 0):,.0f}'
        )

        # Calculer le pourcentage total
        total_montants = total_row.get("total_montants_inscrits", 0)
        total_consomme = total_row.get("total_montant_cumul_2024", 0) + total_row.get(
            "total_montant_2025", 0
        )
        pourcentage_total = (
            (total_consomme / total_montants * 100) if total_montants > 0 else 0
        )
        sheet[f"N{self._current_row}"] = f"{pourcentage_total:.1f}%"

        sheet[f"O{self._current_row}"] = f"{total_montants - total_consomme:,.0f}"
        sheet[f"P{self._current_row}"] = (
            total_row.get("total_aides_inscrits", 0)
            - total_row.get("total_aides_cumul_2024", 0)
            - total_row.get("total_aides_2025", 0)
        )

        # Appliquer le formatage à la ligne des totaux
        for col in [
            "A",
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
        ]:
            cell = sheet[f"{col}{self._current_row}"]
            cell.font = Font(name="Arial", size=9, bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = Border(
                left=Side(style="thin"),
                right=Side(style="thin"),
                top=Side(style="thin"),
                bottom=Side(style="thin"),
            )
            # Fond jaune pour la ligne de total
            cell.fill = PatternFill(
                start_color="FFFF00", end_color="FFFF00", fill_type="solid"
            )

    def _finalize_formatting(self, sheet: Worksheet) -> None:
        self._logger.debug("Application du formatage final")

        # Définir les largeurs de colonnes
        column_widths: dict[str, int] = {
            "A": 15,  # DAIRA
            "B": 20,  # COMMUNES
            "C": 12,  # NB TOTAL
            "D": 12,  # NB AIDES BNH
            "E": 15,  # MONTANTS INSCRITS
            "F": 12,  # NB AIDES LANCÉS
            "G": 15,  # MONTANTS DÉCRITS
            "H": 12,  # NB AIDES MDV
            "I": 15,  # MONTANTS MDV
            "J": 12,  # NB CUMUL 2024
            "K": 15,  # MONTANT CUMUL 2024
            "L": 12,  # NB 2025
            "M": 15,  # MONTANT 2025
            "N": 10,  # % CONSOMMÉ
            "O": 18,  # SOLDE MONTANT
            "P": 12,  # RESTE NOMBRE
        }

        for col, width in column_widths.items():
            sheet.column_dimensions[col].width = width

        # Configuration de la page
        sheet.page_setup.orientation = "landscape"
        sheet.page_setup.fitToWidth = 1
        sheet.page_setup.fitToHeight = 0
        sheet.page_margins.left = 0.5
        sheet.page_margins.right = 0.5
        sheet.page_margins.top = 0.5
        sheet.page_margins.bottom = 0.5

        self._logger.info("Formatage final terminé avec succès")
