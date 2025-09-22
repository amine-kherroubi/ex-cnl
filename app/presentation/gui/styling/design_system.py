from __future__ import annotations


from enum import IntEnum, StrEnum
from typing import Final, final

_BASE: Final[int] = 5


@final
class DesignSystem(object):
    class Color(StrEnum):
        BLUE = "#1976d2"
        LIGHTER_BLUE = "#42a5f5"
        DARKER_BLUE = "#1565c0"
        DARKEST_BLUE = "#0d47a1"

        GRAY = "#757575"
        LIGHTER_GRAY = "#9e9e9e"
        DARKER_GRAY = "#424242"

        BLACK = "#212121"
        WHITE = "#ffffff"
        LESS_WHITE = "#ececec"
        LEAST_WHITE = "#dbdbdb"

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
