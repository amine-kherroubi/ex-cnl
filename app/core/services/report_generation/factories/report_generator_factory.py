from __future__ import annotations

# Standard library imports
from logging import Logger
from typing import final

# Local application imports
from app.core.domain.models.report_context import ReportContext
from app.core.domain.models.report_specification import ReportSpecification
from app.core.domain.registry.report_specification_registry import (
    ReportSpecificationRegistry,
)
from app.core.infrastructure.data.data_repository import DataRepository
from app.core.infrastructure.file_io.file_io_service import FileIOService
from app.core.services.report_generation.generators.activite_mensuelle_hr import (
    ActiviteMensuelleHRGenerator,
)
from app.core.services.report_generation.base.report_generator import ReportGenerator
from app.core.utils.logging_setup import get_logger


@final
class ReportGeneratorFactory(object):
    __slots__ = ()

    _logger: Logger = get_logger(__name__)

    _generators: dict[str, type[ReportGenerator]] = {
        "activite_mensuelle_par_programme": ActiviteMensuelleHRGenerator,
    }

    def __new__(cls):
        raise RuntimeError(
            f"{cls.__name__} is not intended to be instantiated. Use class methods"
        )

    @classmethod
    def create_generator(
        cls,
        report_name: str,
        file_io_service: FileIOService,
        data_repository: DataRepository,
        report_context: ReportContext,
    ) -> ReportGenerator:
        cls._logger.info(f"Creating generator for report: {report_name}")
        cls._logger.debug(f"Available generators: {list(cls._generators.keys())}")

        if report_name not in cls._generators:
            error_msg: str = f"Unknown report: {report_name}"
            cls._logger.error(f"{error_msg}. Available: {list(cls._generators.keys())}")
            raise ValueError(error_msg)

        try:
            report_specification: ReportSpecification = ReportSpecificationRegistry.get(
                report_name
            )
            cls._logger.debug(
                f"Retrieved report specification: {report_specification.display_name}"
            )

            generator_class: type[ReportGenerator] = cls._generators[report_name]
            cls._logger.debug(f"Using generator class: {generator_class.__name__}")

            generator: ReportGenerator = generator_class(
                file_io_service,
                data_repository,
                report_specification,
                report_context,
            )

            cls._logger.info(
                f"{generator_class.__name__} created successfully for report '{report_name}'"
            )
            cls._logger.debug(
                f"Generator context: wilaya={report_context.wilaya.value}, date={report_context.report_date}"
            )

            return generator

        except Exception as error:
            cls._logger.exception(
                f"Failed to create generator for report '{report_name}': {error}"
            )
            raise
