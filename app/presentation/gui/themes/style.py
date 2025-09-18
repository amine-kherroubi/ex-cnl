from __future__ import annotations

# Standard library import
from enum import IntEnum, StrEnum


class Color(StrEnum):
    # Primary Colors - Blue Palette
    PRIMARY = "#1976d2"  # Material Blue 700
    PRIMARY_HOVER = "#1565c0"  # Material Blue 800
    PRIMARY_LIGHT = "#42a5f5"  # Material Blue 400
    PRIMARY_DARK = "#0d47a1"  # Material Blue 900

    # Secondary Colors
    SECONDARY = "#757575"  # Medium Gray for secondary text
    SECONDARY_LIGHT = "#9e9e9e"  # Light Gray for disabled states
    SECONDARY_DARK = "#424242"  # Dark Gray

    # Background Colors
    BACKGROUND_PRIMARY = "#ffffff"  # Pure white
    BACKGROUND_SECONDARY = "#fafbfc"  # Very light gray
    BACKGROUND_TERTIARY = "#f5f7fa"  # Light gray for cards

    # Text Colors
    TEXT_PRIMARY = "#212121"  # Near black for primary text
    TEXT_SECONDARY = "#757575"  # Medium gray for secondary text
    TEXT_DISABLED = "#9e9e9e"  # Light gray for disabled text
    TEXT_ON_PRIMARY = "#ffffff"  # White text on primary background

    # Border Colors
    BORDER_LIGHT = "#e0e0e0"  # Light border
    BORDER_MEDIUM = "#bdbdbd"  # Medium border
    BORDER_DARK = "#757575"  # Dark border

    # State Colors
    SUCCESS = "#4caf50"  # Material Green 500
    WARNING = "#ff9800"  # Material Orange 500
    ERROR = "#f44336"  # Material Red 500
    INFO = "#2196f3"  # Material Blue 500

    # Transparent
    TRANSPARENT = "transparent"


class FontSize(IntEnum):
    # Headings
    HEADING_LARGE = 24  # Main titles
    HEADING_MEDIUM = 20  # Section titles
    HEADING_SMALL = 18  # Subsection titles

    # Body Text
    BODY_LARGE = 16  # Large body text
    BODY_MEDIUM = 14  # Standard body text
    BODY_SMALL = 13  # Small body text

    # UI Elements
    BUTTON = 14  # Button text
    LABEL = 13  # Form labels
    CAPTION = 12  # Captions and hints


class Spacing(IntEnum):
    # Base spacing unit (8px grid system)
    BASE = 8

    # Common spacing values
    XS = BASE // 2  # 4px
    SM = BASE  # 8px
    MD = BASE * 2  # 16px
    LG = BASE * 3  # 24px
    XL = BASE * 4  # 32px
    XXL = BASE * 6  # 48px

    # Semantic spacing
    PADDING_SMALL = SM  # 8px
    PADDING_MEDIUM = MD  # 16px
    PADDING_LARGE = LG  # 24px

    MARGIN_SMALL = SM  # 8px
    MARGIN_MEDIUM = MD  # 16px
    MARGIN_LARGE = LG  # 24px
