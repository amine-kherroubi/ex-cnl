from __future__ import annotations

# Standard library imports
from datetime import date

# Local application imports
from app.core.domain.enums.space_time import Month


class DateFormattingService(object):
    __slots__ = ()

    def __new__(cls):
        raise RuntimeError("DateFormatter cannot be instantiated. Use class methods.")

    @classmethod
    def to_french_month_year(cls, month: Month, year: int) -> str:

        return f"{month.upper()} {year}"

    @classmethod
    def to_french_date_range(cls, month: Month, year: int) -> str:

        month_name = month.upper()
        last_day = month.last_day(year)
        return f"de {month_name} au {last_day} {month_name} {year}"

    @classmethod
    def to_french_short_date(cls, report_date: date) -> str:

        return report_date.strftime("%d/%m/%Y")

    @classmethod
    def to_french_filename_date(cls, report_date: date) -> str:

        return report_date.strftime("%d_%m_%Y")

    @classmethod
    def to_iso_date(cls, report_date: date) -> str:

        return report_date.strftime("%Y-%m-%d")
