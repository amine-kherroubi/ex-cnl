from __future__ import annotations

# Standard library imports
from typing import Any, Literal, final

# Third-party imports
from openpyxl.styles import Alignment, Border, Font, Side
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils import get_column_letter


@final
class ExcelStylingService(object):

    FONT_NORMAL = Font(name="Arial", size=9, bold=False)
    FONT_BOLD = Font(name="Arial", size=9, bold=False)
    FONT_HEADER = Font(name="Arial", size=9, bold=False)
    FONT_TITLE = Font(name="Arial", size=9, bold=False)

    BORDER_THIN = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )

    ALIGNMENT_CENTER = Alignment(horizontal="center", vertical="center")
    ALIGNMENT_CENTER_WRAP = Alignment(
        horizontal="center", vertical="center", wrap_text=True
    )
    ALIGNMENT_LEFT = Alignment(horizontal="left", vertical="center")
    ALIGNMENT_RIGHT = Alignment(horizontal="right", vertical="center")

    @classmethod
    def apply_style_to_cell(
        cls,
        sheet: Worksheet,
        col: str,
        row: int,
        font: Font | None = None,
        alignment: Alignment | None = None,
        border: Border | None = None,
        value: Any = None,
    ) -> None:
        font = font or cls.FONT_NORMAL
        alignment = alignment or cls.ALIGNMENT_CENTER

        cell = sheet[f"{col}{row}"]
        if value is not None:
            cell.value = value
        cell.font = font
        cell.alignment = alignment
        if border:
            cell.border = border

    @classmethod
    def merge_and_style_cells(
        cls,
        sheet: Worksheet,
        start_col: str,
        end_col: str,
        start_row: int,
        end_row: int,
        value: Any = None,
        font: Font | None = None,
        alignment: Alignment | None = None,
        border: Border | None = None,
    ) -> None:

        if value is not None:
            sheet[f"{start_col}{start_row}"] = value

        sheet.merge_cells(f"{start_col}{start_row}:{end_col}{end_row}")

        font = font or cls.FONT_NORMAL
        alignment = alignment or cls.ALIGNMENT_CENTER

        start_col_idx: int = ord(start_col) - ord("A") + 1
        end_col_idx: int = ord(end_col) - ord("A") + 1

        for row in range(start_row, end_row + 1):
            for col_idx in range(start_col_idx, end_col_idx + 1):
                col_letter: str = get_column_letter(col_idx)
                cell = sheet[f"{col_letter}{row}"]
                cell.font = font
                cell.alignment = alignment
                if border:
                    cell.border = border

    @classmethod
    def set_column_widths(cls, sheet: Worksheet, column_widths: dict[str, int]) -> None:
        for col, width in column_widths.items():
            sheet.column_dimensions[col].width = width

    @classmethod
    def setup_page_layout(
        cls,
        sheet: Worksheet,
        orientation: Literal["portrait", "landscape"] = "portrait",
        fit_to_width: bool = True,
        fit_to_height: bool = False,
    ) -> None:
        sheet.page_setup.orientation = orientation
        if fit_to_width:
            sheet.page_setup.fitToWidth = 1
        if fit_to_height:
            sheet.page_setup.fitToHeight = 1
        if not fit_to_height:
            sheet.page_setup.fitToHeight = 0

    @classmethod
    def setup_page_margins(
        cls,
        sheet: Worksheet,
        left: float = 0.25,
        right: float = 0.25,
        top: float = 0.5,
        bottom: float = 0.5,
    ) -> None:
        sheet.page_margins.left = left
        sheet.page_margins.right = right
        sheet.page_margins.top = top
        sheet.page_margins.bottom = bottom

    @classmethod
    def apply_data_row_styling(
        cls,
        sheet: Worksheet,
        row: int,
        data: list[tuple[str, Any]],
        font: Font | None = None,
        alignment: Alignment | None = None,
        border: Border | None = None,
    ) -> None:
        font = font or cls.FONT_NORMAL
        alignment = alignment or cls.ALIGNMENT_CENTER

        for col, value in data:
            cls.apply_style_to_cell(sheet, col, row, font, alignment, border, value)
