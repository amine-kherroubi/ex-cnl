from __future__ import annotations

# Third-party imports
import pandas
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

# Local application imports
from app.services.document_generation.document_generator_template import (
    DocumentGenerator,
)


class ActiviteMensuelleHRGenerator(DocumentGenerator):
    __slots__ = ()

    def _add_header(self, sheet: Worksheet) -> None:
        self._logger.debug("Adding document header")

        # HABITAT RURAL - Set value first, then merge
        sheet["A1"] = "HABITAT RURAL"
        sheet.merge_cells("A1:E1")
        sheet["A1"].font = Font(name="Arial", size=9, bold=True)
        sheet["A1"].alignment = Alignment(horizontal="center", vertical="center")
        self._logger.debug("Added main title: HABITAT RURAL")

        # Wilaya
        wilaya_text = f"WILAYA DE : {self._document_context.wilaya.value.upper()}"
        sheet["A2"] = wilaya_text
        sheet["A2"].font = Font(name="Arial", size=9, bold=True)
        self._logger.debug(f"Added wilaya: {wilaya_text}")

        # Main title - Set value first, then merge
        sheet["B3"] = (
            "ACTIVITE MENSUELLE PAR PROGRAMMES (À renseigner par la BNH (ex-CNL))"
        )
        sheet.merge_cells("B3:D3")
        sheet["B3"].font = Font(name="Arial", size=9, bold=True)
        sheet["B3"].alignment = Alignment(
            horizontal="center", vertical="center", wrap_text=True
        )
        self._logger.debug("Added document title")

        # Month - Set value first, then merge
        month_text: str = (
            f"MOIS DE {self._document_context.month.value.upper()} {self._document_context.year}"
        )
        sheet["A4"] = month_text
        sheet.merge_cells("A4:E4")
        sheet["A4"].font = Font(name="Arial", size=9, bold=True)
        sheet["A4"].alignment = Alignment(horizontal="center", vertical="center")
        self._logger.debug(f"Added month and year: {month_text}")

        self._logger.info("Document header completed successfully")

    def _add_table(
        self, sheet: Worksheet, query_results: dict[str, pandas.DataFrame]
    ) -> None:
        self._logger.debug("Adding main data table")
        self._logger.debug(f"Available query results: {list(query_results.keys())}")

        start_row: int = 6

        # Caption row (part of table) - Set value first, then merge
        caption_text: str = (
            f"ETAT D'EXECUTION DES TRANCHES FINANCIERES DURANT LE MOIS DE {self._document_context.month.value.upper()} {self._document_context.year}"
        )
        sheet[f"A{start_row}"] = caption_text
        sheet.merge_cells(f"A{start_row}:E{start_row}")
        sheet[f"A{start_row}"].font = Font(name="Arial", size=9, bold=True)
        sheet[f"A{start_row}"].alignment = Alignment(
            horizontal="center", vertical="center", wrap_text=True
        )
        sheet[f"A{start_row}"].fill = PatternFill(
            start_color="D9E2F3", end_color="D9E2F3", fill_type="solid"
        )
        self._logger.debug("Added table caption")

        # Headers
        header_row: int = start_row + 2
        headers: list[tuple[str, str]] = [
            ("A", "PROGRAMMES"),
            ("B", "LIVRAISONS (libération de la dernière TR)"),
            ("C", "CUMUL LIVRAISONS"),
            ("D", "LANCEMENTS (libération de la 1ère TR)"),
            ("E", "CUMUL LANCEMENTS"),
        ]

        self._logger.debug(f"Adding {len(headers)} column headers at row {header_row}")
        for col, title in headers:
            cell = sheet[f"{col}{header_row}"]
            cell.value = title
            cell.font = Font(name="Arial", size=9, bold=True)
            cell.alignment = Alignment(
                horizontal="center", vertical="center", wrap_text=True
            )
            cell.fill = PatternFill(
                start_color="366092", end_color="366092", fill_type="solid"
            )
            cell.border = Border(
                left=Side(style="thin"),
                right=Side(style="thin"),
                top=Side(style="thin"),
                bottom=Side(style="thin"),
            )

        # Sub-headers
        sub_row: int = header_row + 1
        month_short: str = self._document_context.month.value[:3].title()
        year_short: str = str(self._document_context.year)[-2:]

        sheet[f"B{sub_row}"] = f"{month_short}-{year_short}"
        sheet[f"C{sub_row}"] = (
            f"Cumul de JANVIER au 31 {self._document_context.month.value.upper()} {self._document_context.year}"
        )
        sheet[f"D{sub_row}"] = f"{month_short}-{year_short}"
        sheet[f"E{sub_row}"] = (
            f"Cumul de JANVIER au 31 {self._document_context.month.value.upper()} {self._document_context.year}"
        )

        for col in ["B", "C", "D", "E"]:
            cell = sheet[f"{col}{sub_row}"]
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
        self._logger.debug("Added sub-headers with date ranges")

        # Add data from query results
        data_start_row: int = sub_row + 1
        self._logger.debug(f"Starting data rows at row {data_start_row}")

        # Get all programmes first
        all_programmes: list[str] = []
        if "all_programmes" in query_results:
            all_programmes = query_results["all_programmes"]["Programme"].tolist()
            self._logger.info(
                f"Found {len(all_programmes)} programmes: {all_programmes}"
            )
        else:
            self._logger.warning("No 'all_programmes' query result found")

        # Create lookup dictionaries for each metric
        self._logger.debug("Creating lookup dictionaries from query results")

        lancements_month_dict: dict[str, int] = {}
        if "lancements_month" in query_results:
            df_lm: pandas.DataFrame = query_results["lancements_month"]
            lancements_month_dict = dict(zip(df_lm["Programme"], df_lm["Count"]))
            self._logger.debug(
                f"Lancements month data: {len(lancements_month_dict)} programmes"
            )
        else:
            self._logger.warning("No 'lancements_month' query result found")

        lancements_ytd_dict: dict[str, int] = {}
        if "lancements_ytd" in query_results:
            df_ly: pandas.DataFrame = query_results["lancements_ytd"]
            lancements_ytd_dict = dict(zip(df_ly["Programme"], df_ly["Count"]))
            self._logger.debug(
                f"Lancements YTD data: {len(lancements_ytd_dict)} programmes"
            )
        else:
            self._logger.warning("No 'lancements_ytd' query result found")

        livraisons_month_dict: dict[str, int] = {}
        if "livraisons_month" in query_results:
            df_livm: pandas.DataFrame = query_results["livraisons_month"]
            livraisons_month_dict = dict(zip(df_livm["Programme"], df_livm["Count"]))
            self._logger.debug(
                f"Livraisons month data: {len(livraisons_month_dict)} programmes"
            )
        else:
            self._logger.warning("No 'livraisons_month' query result found")

        livraisons_ytd_dict: dict[str, int] = {}
        if "livraisons_ytd" in query_results:
            df_livy: pandas.DataFrame = query_results["livraisons_ytd"]
            livraisons_ytd_dict = dict(zip(df_livy["Programme"], df_livy["Count"]))
            self._logger.debug(
                f"Livraisons YTD data: {len(livraisons_ytd_dict)} programmes"
            )
        else:
            self._logger.warning("No 'livraisons_ytd' query result found")

        # Calculate totals
        total_livraisons_month: int = sum(livraisons_month_dict.values())
        total_livraisons_ytd: int = sum(livraisons_ytd_dict.values())
        total_lancements_month: int = sum(lancements_month_dict.values())
        total_lancements_ytd: int = sum(lancements_ytd_dict.values())

        self._logger.info(
            f"Calculated totals - Livraisons: {total_livraisons_month} (month), {total_livraisons_ytd} (YTD)"
        )
        self._logger.info(
            f"Calculated totals - Lancements: {total_lancements_month} (month), {total_lancements_ytd} (YTD)"
        )

        # Add data rows for each programme
        self._logger.debug(f"Adding data rows for {len(all_programmes)} programmes")
        for i, programme in enumerate(all_programmes):
            row: int = data_start_row + i
            self._logger.debug(f"Processing programme '{programme}' at row {row}")

            # Column A: Programme name
            sheet[f"A{row}"] = programme
            sheet[f"A{row}"].font = Font(name="Arial", size=9)

            # Column B: Livraisons (Month)
            livraisons_month: int = livraisons_month_dict.get(programme, 0)
            sheet[f"B{row}"] = livraisons_month
            sheet[f"B{row}"].font = Font(name="Arial", size=9)

            # Column C: Livraisons (YTD)
            livraisons_ytd: int = livraisons_ytd_dict.get(programme, 0)
            sheet[f"C{row}"] = livraisons_ytd
            sheet[f"C{row}"].font = Font(name="Arial", size=9)

            # Column D: Lancements (Month)
            lancements_month: int = lancements_month_dict.get(programme, 0)
            sheet[f"D{row}"] = lancements_month
            sheet[f"D{row}"].font = Font(name="Arial", size=9)

            # Column E: Lancements (YTD)
            lancements_ytd: int = lancements_ytd_dict.get(programme, 0)
            sheet[f"E{row}"] = lancements_ytd
            sheet[f"E{row}"].font = Font(name="Arial", size=9)

            # Add borders
            for col in ["A", "B", "C", "D", "E"]:
                cell = sheet[f"{col}{row}"]
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = Border(
                    left=Side(style="thin"),
                    right=Side(style="thin"),
                    top=Side(style="thin"),
                    bottom=Side(style="thin"),
                )

            if (
                livraisons_month > 0
                or lancements_month > 0
                or livraisons_ytd > 0
                or lancements_ytd > 0
            ):
                self._logger.debug(
                    f"Programme '{programme}': L={livraisons_month}/{livraisons_ytd}, La={lancements_month}/{lancements_ytd}"
                )

        # Add TOTAL row
        total_row_index: int = data_start_row + len(all_programmes)
        self._logger.debug(f"Adding TOTAL row at row {total_row_index}")

        sheet[f"A{total_row_index}"] = "TOTAL"
        sheet[f"B{total_row_index}"] = total_livraisons_month
        sheet[f"C{total_row_index}"] = total_livraisons_ytd
        sheet[f"D{total_row_index}"] = total_lancements_month
        sheet[f"E{total_row_index}"] = total_lancements_ytd

        # Format TOTAL row
        for col in ["A", "B", "C", "D", "E"]:
            cell = sheet[f"{col}{total_row_index}"]
            cell.font = Font(name="Arial", size=9, bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.fill = PatternFill(
                start_color="E7E6E6", end_color="E7E6E6", fill_type="solid"
            )
            cell.border = Border(
                left=Side(style="thin"),
                right=Side(style="thin"),
                top=Side(style="thin"),
                bottom=Side(style="thin"),
            )

        self._logger.info(
            f"Main table completed with {len(all_programmes)} programmes plus totals"
        )

    def _add_footer(self, sheet: Worksheet) -> None:
        self._logger.debug("Adding document footer")
        # No footer for this document type
        self._logger.debug("No footer required for this document type")

    def _finalize_formatting(self, sheet: Worksheet) -> None:
        self._logger.debug("Applying final formatting")

        column_widths: dict[str, int] = {"A": 25, "B": 18, "C": 22, "D": 18, "E": 22}
        self._logger.debug(f"Setting column widths: {column_widths}")

        for col, width in column_widths.items():
            sheet.column_dimensions[col].width = width

        sheet.page_setup.orientation = "portrait"
        sheet.page_setup.fitToWidth = 1
        sheet.page_setup.fitToHeight = 0

        self._logger.debug("Set page orientation to portrait with fit to width")
        self._logger.info("Final formatting completed successfully")
