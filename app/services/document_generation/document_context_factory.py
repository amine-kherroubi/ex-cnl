from __future__ import annotations

# Standard library imports
from datetime import date

# Local application imports
from app.services.document_generation.models.document_context import (
    DocumentContext,
)
from app.utils.space_time import Periodicity, Month, Wilaya


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
        today: date = date.today()
        year = year or today.year
        month = month or Month.from_number(today.month)

        if report_date is None:
            # Default to end of month
            last_day: int = month.last_day(year)
            report_date = date(year, month.number, last_day)

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
            end_month_number = 6 if semester == 1 else 12
            last_day: int = Month.from_number(end_month_number).last_day(year)
            report_date = date(year, end_month_number, last_day)

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
