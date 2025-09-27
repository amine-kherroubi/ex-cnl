# Standard library imports
from enum import Enum
from typing import Final, final
import colorsys
import platform

_BASE: Final[int] = 6
_SYSTEM: Final[str] = platform.system()


def adjust_color(hex_color: str, factor: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = [int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = max(0, min(1, l * factor))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


@final
class DesignSystem(object):
    class Color(Enum):
        PRIMARY = "#adad00"
        LIGHTER_PRIMARY = adjust_color(PRIMARY, 1.6)
        DARKER_PRIMARY = adjust_color(PRIMARY, 0.8)

        GRAY = "#757575"
        LIGHTER_GRAY = adjust_color(GRAY, 1.6)
        DARKER_GRAY = adjust_color(GRAY, 0.8)

        WHITE = "#ffffff"
        LESS_WHITE = adjust_color(WHITE, 0.98)
        LEAST_WHITE = adjust_color(WHITE, 0.95)

        BLACK = "#212121"

        SUCCESS = "#009a05"
        WARNING = "#939300"
        ERROR = "#b50c00"
        INFO = "#212121"

        TRANSPARENT = "transparent"

    class FontSize(Enum):
        H1 = 24
        H2 = 22
        H3 = 20
        H4 = 18
        BODY = 16
        BUTTON = 16
        CAPTION = 14

    class Spacing(Enum):
        NONE = _BASE * 0
        XS = _BASE * 1
        SM = _BASE * 2
        MD = _BASE * 3
        LG = _BASE * 4
        XL = _BASE * 5
        XXL = _BASE * 6

    class Roundness(Enum):
        NONE = 0
        XS = 4
        SM = 6
        MD = 8

    class Width(Enum):
        NONE = 0
        XS = 36
        SM = 100
        MD = 200

    class Height(Enum):
        NONE = 0
        SM = 36

    class BorderWidth(Enum):
        NONE = 0
        XS = 1

    class FontFamily(Enum):
        NORMAL = (
            "SF Pro Display"
            if _SYSTEM == "Darwin"
            else (
                "Segoe UI"
                if _SYSTEM == "Windows"
                else "Ubuntu" if _SYSTEM == "Linux" else "Arial"
            )
        )
        MONO = (
            "Menlo"
            if _SYSTEM == "Darwin"
            else ("Consolas" if _SYSTEM == "Windows" else "Monospace")
        )
