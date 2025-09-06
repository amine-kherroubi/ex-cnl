from __future__ import annotations

# Standard library imports
from datetime import date

# Local application imports
from app.services.document_generation.context_management.document_context import (
    DocumentContext,
)
from app.utils.space_time import (
    Periodicity,
    get_last_day_of_month,
    Month,
    month_to_numeric,
    numeric_to_month,
    Wilaya,
)


class DocumentContextFactory(object):
    __slots__ = ()

    def __new__(cls):
        raise RuntimeError(
            "DocumentContextFactory cannot be instantiated. Use class methods."
        )

    @classmethod
    def create_context(
        cls,
        wilaya: Wilaya,
        year: int | None = None,
        periodicity: Periodicity | None = None,
        month: Month | None = None,
        semester: int | None = None,
        report_date: date | None = None,
    ) -> DocumentContext:
        periodicity = periodicity or Periodicity.MONTHLY

        match periodicity:
            case Periodicity.MONTHLY:
                return cls._monthly(wilaya, year, month, report_date)
            case Periodicity.SEMIANNUAL:
                return cls._semiannual(wilaya, year, semester, report_date)
            case Periodicity.ANNUAL:
                return cls._annual(wilaya, year, report_date)
            case _:
                raise ValueError(f"Unknown periodicity: {periodicity}")

    @staticmethod
    def _monthly(
        wilaya: Wilaya, year: int | None, month: Month | None, report_date: date | None
    ) -> DocumentContext:
        today = date.today()
        year = year or today.year
        month = month or numeric_to_month(today.month)

        if report_date is None:
            # Default to end of month
            last_day = get_last_day_of_month(year, month)
            report_date = date(year, month_to_numeric(month), last_day)

        return DocumentContext(
            wilaya=wilaya,
            year=year,
            report_date=report_date,
            month=month,
        )

    @staticmethod
    def _semiannual(
        wilaya: Wilaya, year: int | None, semester: int | None, report_date: date | None
    ) -> DocumentContext:
        today = date.today()
        year = year or today.year
        semester = semester or (1 if today.month <= 6 else 2)

        if report_date is None:
            # Default to end of semester
            end_month = 6 if semester == 1 else 12
            last_day = get_last_day_of_month(year, numeric_to_month(end_month))
            report_date = date(year, end_month, last_day)

        return DocumentContext(
            wilaya=wilaya, year=year, semester=semester, report_date=report_date
        )

    @staticmethod
    def _annual(
        wilaya: Wilaya, year: int | None, report_date: date | None
    ) -> DocumentContext:
        today = date.today()
        year = year or today.year

        if report_date is None:
            report_date = date(year, 12, 31)

        return DocumentContext(wilaya=wilaya, year=year, report_date=report_date)
