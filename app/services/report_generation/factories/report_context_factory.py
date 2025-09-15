from __future__ import annotations

# Standard library imports
from datetime import date
from logging import Logger
from typing import final

# Local application imports
from app.services.report_generation.models.report_context import (
    ReportContext,
)
from app.services.report_generation.enums.space_time import Periodicity, Month, Wilaya
from app.utils.logging_setup import get_logger


@final
class ReportContextFactory(object):
    __slots__ = ()

    _logger: Logger = get_logger(__name__)

    def __new__(cls):
        raise RuntimeError(
            f"{cls.__name__} is not intended to be instantiated. Use class methods"
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
    ) -> ReportContext:
        cls._logger.info(f"Creating report context for wilaya: {wilaya.value}")
        cls._logger.debug(
            f"Parameters: year={year}, periodicity={periodicity}, month={month}, semester={semester}, report_date={report_date}"
        )

        periodicity = periodicity or Periodicity.MONTHLY
        cls._logger.debug(f"Using periodicity: {periodicity.value}")

        try:
            match periodicity:
                case Periodicity.MONTHLY:
                    cls._logger.debug("Creating monthly report context")
                    context = cls._monthly(wilaya, year, month, report_date)
                case Periodicity.SEMESTRIAL:
                    cls._logger.debug("Creating semiannual report context")
                    context = cls._semiannual(wilaya, year, semester, report_date)
                case Periodicity.ANNUAL:
                    cls._logger.debug("Creating annual report context")
                    context = cls._annual(wilaya, year, report_date)
                case _:
                    error_msg = f"Unknown periodicity: {periodicity}"
                    cls._logger.error(error_msg)
                    raise ValueError(error_msg)

            cls._logger.info(
                f"{periodicity.value.capitalize()} context created successfully for {wilaya.value} - {context.report_date}"
            )
            return context

        except Exception as error:
            cls._logger.exception(f"Failed to create report context: {error}")
            raise

    @staticmethod
    def _monthly(
        wilaya: Wilaya, year: int | None, month: Month | None, report_date: date | None
    ) -> ReportContext:
        logger: Logger = ReportContextFactory._logger
        logger.debug("Processing monthly context parameters")

        today: date = date.today()
        year = year or today.year
        month = month or Month.from_number(today.month)

        logger.debug(f"Resolved year: {year}, month: {month.value}")

        if report_date is None:
            last_day: int = month.last_day(year)
            report_date = date(year, month.number, last_day)
            logger.debug(
                f"Generated default report date: {report_date} (end of {month.value})"
            )
        else:
            logger.debug(f"Using provided report date: {report_date}")

        context = ReportContext(
            wilaya=wilaya,
            year=year,
            report_date=report_date,
            month=month,
        )

        logger.info(f"Monthly context created: {wilaya.value}, {month.value} {year}")
        return context

    @staticmethod
    def _semiannual(
        wilaya: Wilaya, year: int | None, semester: int | None, report_date: date | None
    ) -> ReportContext:
        logger: Logger = ReportContextFactory._logger
        logger.debug("Processing semiannual context parameters")

        today: date = date.today()
        year = year or today.year
        semester = semester or (1 if today.month <= 6 else 2)

        logger.debug(f"Resolved year: {year}, semester: {semester}")

        if report_date is None:
            end_month_number = 6 if semester == 1 else 12
            last_day: int = Month.from_number(end_month_number).last_day(year)
            report_date = date(year, end_month_number, last_day)
            logger.debug(
                f"Generated default report date: {report_date} (end of semester {semester})"
            )
        else:
            logger.debug(f"Using provided report date: {report_date}")

        context: ReportContext = ReportContext(
            wilaya=wilaya, year=year, semester=semester, report_date=report_date
        )

        logger.info(
            f"Semiannual context created: {wilaya.value}, semester {semester} of {year}"
        )
        return context

    @staticmethod
    def _annual(
        wilaya: Wilaya, year: int | None, report_date: date | None
    ) -> ReportContext:
        logger: Logger = ReportContextFactory._logger
        logger.debug("Processing annual context parameters")

        today: date = date.today()
        year = year or today.year

        logger.debug(f"Resolved year: {year}")

        if report_date is None:
            report_date = date(year, 12, 31)
            logger.debug(f"Generated default report date: {report_date} (end of year)")
        else:
            logger.debug(f"Using provided report date: {report_date}")

        context: ReportContext = ReportContext(
            wilaya=wilaya, year=year, report_date=report_date
        )

        logger.info(f"Annual context created: {wilaya.value}, year {year}")
        return context
