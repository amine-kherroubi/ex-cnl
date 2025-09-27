# Standard library imports
from typing import Final, final, List, Dict
from logging import Logger

# Local application imports
from app.core.domain.models.report_specification import ReportSpecification
from app.core.domain.predefined_objects.report_specifications import (
    activite_mensuelle_specification,
    situation_financiere_specification,
)
from app.common.logging_setup import get_logger


@final
class ReportSpecificationRegistry(object):
    __slots__ = ()

    _logger: Logger = get_logger(__name__)

    def __new__(cls):
        raise RuntimeError(
            f"{cls.__name__} is not intended to be instantiated. Use class methods"
        )

    @classmethod
    def get(cls, report_name: str) -> ReportSpecification:
        cls._logger.debug(f"Retrieving specification for report: {report_name}")

        for report_spec in cls._REPORT_SPECIFICATIONS:
            if report_spec.name == report_name:
                cls._logger.info(
                    f"Retrieved specification for report '{report_name}': {report_spec.display_name}"
                )
                return report_spec

        available: List[str] = [r.name for r in cls._REPORT_SPECIFICATIONS]
        error_msg = f"Report '{report_name}' not found. Available: {available}"
        cls._logger.error(error_msg)
        raise ValueError(error_msg)

    @classmethod
    def has(cls, report_name: str) -> bool:
        cls._logger.debug(f"Checking existence of report: {report_name}")
        exists = any(r.name == report_name for r in cls._REPORT_SPECIFICATIONS)
        cls._logger.debug(f"Report '{report_name}' exists: {exists}")
        return exists

    @classmethod
    def all(cls) -> Dict[str, ReportSpecification]:
        cls._logger.debug("Retrieving all report specifications")
        specifications = {r.name: r for r in cls._REPORT_SPECIFICATIONS}
        cls._logger.info(f"Retrieved {len(specifications)} report specifications")
        return specifications

    _REPORT_SPECIFICATIONS: Final[List[ReportSpecification]] = [
        activite_mensuelle_specification,
        situation_financiere_specification,
    ]
