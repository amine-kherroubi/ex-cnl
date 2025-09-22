from __future__ import annotations
from typing import Literal

from openpyxl.styles import Alignment, Border, Font, Side
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils import get_column_letter


# Font constants for consistency
FONT_NORMAL = Font(name="Arial", size=9, bold=False)
FONT_BOLD = Font(name="Arial", size=9, bold=True)
FONT_HEADER = Font(name="Arial", size=10, bold=True)
FONT_TITLE = Font(name="Arial", size=12, bold=True)

# Border constants
BORDER_THIN = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)

# Alignment constants
ALIGNMENT_CENTER = Alignment(horizontal="center", vertical="center")
ALIGNMENT_CENTER_WRAP = Alignment(
    horizontal="center", vertical="center", wrap_text=True
)
ALIGNMENT_LEFT = Alignment(horizontal="left", vertical="center")
ALIGNMENT_RIGHT = Alignment(horizontal="right", vertical="center")


def apply_style_to_merged_cells(
    sheet: Worksheet,
    start_col: str,
    start_row: int,
    end_col: str,
    end_row: int,
    font: Font = FONT_NORMAL,
    alignment: Alignment = ALIGNMENT_CENTER,
    border: Border | None = None,
) -> None:
    """Apply consistent styling to all cells in a merged range.

    Args:
        sheet: The worksheet to apply styling to
        start_col: Starting column letter (e.g., 'A')
        start_row: Starting row number
        end_col: Ending column letter (e.g., 'E')
        end_row: Ending row number
        font: Font style to apply
        alignment: Alignment style to apply
        border: Optional border style to apply
    """
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


def set_column_widths(sheet: Worksheet, column_widths: dict[str, int]) -> None:
    """Set column widths for the worksheet.

    Args:
        sheet: The worksheet to apply column widths to
        column_widths: Dictionary mapping column letters to their widths
    """
    for col, width in column_widths.items():
        sheet.column_dimensions[col].width = width


def setup_page_layout(
    sheet: Worksheet,
    orientation: Literal["portrait", "landscape"] = "portrait",
    fit_to_width: bool = True,
) -> None:
    """Setup basic page layout for the worksheet.

    Args:
        sheet: The worksheet to configure
        orientation: Page orientation ("portrait" or "landscape")
        fit_to_width: Whether to fit content to page width
    """
    sheet.page_setup.orientation = orientation
    if fit_to_width:
        sheet.page_setup.fitToWidth = 1
        sheet.page_setup.fitToHeight = 0


def setup_page_margins(
    sheet: Worksheet,
    left: float = 0.25,
    right: float = 0.25,
    top: float = 0.75,
    bottom: float = 0.75,
) -> None:
    """Setup page margins for the worksheet.

    Args:
        sheet: The worksheet to configure
        left: Left margin in inches
        right: Right margin in inches
        top: Top margin in inches
        bottom: Bottom margin in inches
    """
    sheet.page_margins.left = left
    sheet.page_margins.right = right
    sheet.page_margins.top = top
    sheet.page_margins.bottom = bottom
