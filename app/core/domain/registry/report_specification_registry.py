from __future__ import annotations

# Standard library imports
from typing import Final, final
from logging import Logger

# Local application imports
from app.core.domain.models.report_specification import ReportSpecification
from app.core.domain.registry.report_specifications import *
from app.core.utils.logging_setup import get_logger


@final
class ReportSpecificationRegistry:
    __slots__ = ()

    _logger: Logger = get_logger(__name__)

    def __new__(cls):
        raise RuntimeError(
            f"{cls.__name__} is not intended to be instantiated. Use class methods"
        )

    @classmethod
    def get(cls, report_name: str) -> ReportSpecification:
        cls._logger.debug(f"Retrieving specification for report: {report_name}")

        if report_name not in cls._REPORT_SPECIFICATIONS:
            available: list[str] = list(cls._REPORT_SPECIFICATIONS.keys())
            error_msg: str = f"Report '{report_name}' not found. Available: {available}"
            cls._logger.error(error_msg)
            raise ValueError(error_msg)

        specification: ReportSpecification = cls._REPORT_SPECIFICATIONS[report_name]
        cls._logger.info(
            f"Retrieved specification for report '{report_name}': {specification.display_name}"
        )
        return specification

    @classmethod
    def has(cls, report_name: str) -> bool:
        cls._logger.debug(f"Checking existence of report: {report_name}")
        exists: bool = report_name in cls._REPORT_SPECIFICATIONS
        cls._logger.debug(f"Report '{report_name}' exists: {exists}")
        return exists

    @classmethod
    def all(cls) -> dict[str, ReportSpecification]:
        cls._logger.debug("Retrieving all report specifications")
        specifications: dict[str, ReportSpecification] = (
            cls._REPORT_SPECIFICATIONS.copy()
        )
        cls._logger.info(f"Retrieved {len(specifications)} report specifications")
        return specifications

    _REPORT_SPECIFICATIONS: Final[dict[str, ReportSpecification]] = {
        "activite_mensuelle_par_programme": activite_mensuelle_specification,
        "situation_financiere_des_programmes": situation_financiere_specification,
    }
