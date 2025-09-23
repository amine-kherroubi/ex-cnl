from __future__ import annotations

# Standard library imports
from enum import IntEnum, StrEnum
from typing import Final, final
import colorsys

_BASE: Final[int] = 6


def adjust_color(hex_color: str, factor: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = [int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = max(0, min(1, l * factor))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


@final
class DesignSystem(object):
    class Color(StrEnum):
        PRIMARY = "#b3b30b"
        LIGHTER_PRIMARY = adjust_color(PRIMARY, 1.5)
        DARKER_PRIMARY = adjust_color(PRIMARY, 0.5)

        GRAY = "#757575"
        LIGHTER_GRAY = adjust_color(GRAY, 1.5)
        DARKER_GRAY = adjust_color(GRAY, 0.5)

        WHITE = "#ffffff"
        LESS_WHITE = adjust_color(WHITE, 0.98)
        LEAST_WHITE = adjust_color(WHITE, 0.95)

        BLACK = "#212121"

        SUCCESS = "#4caf50"
        WARNING = "#ff9800"
        ERROR = "#f44336"
        INFO = "#2196f3"

        TRANSPARENT = "transparent"

    class FontSize(IntEnum):
        H1 = 22
        H2 = 20
        H3 = 18
        BODY = 16
        BUTTON = 16
        LABEL = 14
        CAPTION = 12

    class Spacing(IntEnum):
        NONE = _BASE * 0
        XS = _BASE * 1
        SM = _BASE * 2
        MD = _BASE * 3
        LG = _BASE * 4
        XL = _BASE * 5
        XXL = _BASE * 6

    class Roundness(IntEnum):
        NORMAL = 8
        SMALL = 6
