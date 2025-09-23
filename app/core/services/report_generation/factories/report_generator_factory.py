from __future__ import annotations

# Standard library imports
from logging import Logger
from typing import Any, final

# Local application imports
from app.core.domain.models.report_context import ReportContext
from app.core.domain.models.report_specification import ReportSpecification
from app.core.domain.registry.report_specification_registry import (
    ReportSpecificationRegistry,
)
from app.core.infrastructure.data.data_repository import DataRepository
from app.core.infrastructure.file_io.file_io_service import FileIOService
from app.core.services.report_generation.generators.activite_mensuelle import (
    ActiviteMensuelleGenerator,
)
from app.core.services.report_generation.base_generator import BaseGenerator
from app.core.services.report_generation.generators.situation_financiere import (
    SituationFinanciereGenerator,
)
from app.core.utils.logging_setup import get_logger


@final
class ReportGeneratorFactory:
    __slots__ = ()

    _logger: Logger = get_logger(__name__)

    _generators: dict[str, type[BaseGenerator]] = {
        "activite_mensuelle_par_programme": ActiviteMensuelleGenerator,
        "situation_financiere_des_programmes": SituationFinanciereGenerator,
    }

    def __new__(cls) -> None:
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
        **kwargs: Any,
    ) -> BaseGenerator:
        """Create a report generator for the specified report.

        Args:
            report_name: Name of the report to generate
            file_io_service: File I/O service instance
            data_repository: Data repository instance
            report_context: Report context with wilaya, date, etc.
            **kwargs: Additional report-specific parameters (e.g., target_programme)

        Returns:
            Configured report generator instance
        """
        cls._logger.info(f"Creating generator for report: {report_name}")
        cls._logger.debug(f"Available generators: {list(cls._generators.keys())}")
        cls._logger.debug(f"Additional parameters: {kwargs}")

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

            generator_class: type[BaseGenerator] = cls._generators[report_name]
            cls._logger.debug(f"Using generator class: {generator_class.__name__}")

            # Create generator with base dependencies
            generator: BaseGenerator = generator_class(
                file_io_service=file_io_service,
                data_repository=data_repository,
                report_specification=report_specification,
                report_context=report_context,
            )

            # Configure generator with additional parameters if supported
            if hasattr(generator, "configure") and kwargs:
                cls._logger.debug("Configuring generator with additional parameters")
                generator.configure(**kwargs)
            elif kwargs:
                cls._logger.warning(
                    f"Additional parameters provided but generator {generator_class.__name__} "
                    f"does not support configuration: {list(kwargs.keys())}"
                )

            cls._logger.info(
                f"{generator_class.__name__} created successfully for report '{report_name}'"
            )

            return generator

        except Exception as error:
            cls._logger.exception(
                f"Failed to create generator for report '{report_name}': {error}"
            )
            raise
