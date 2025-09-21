from __future__ import annotations

# Standard library imports
from logging import Logger
from pathlib import Path

# Local application imports
from app.core.config import AppConfig
from app.core.domain.models.report_context import ReportContext
from app.core.domain.models.report_specification import ReportSpecification
from app.core.domain.registry.report_specification_registry import (
    ReportSpecificationRegistry,
)
from app.core.infrastructure.data.data_repository import DuckDBRepository
from app.core.infrastructure.file_io.file_io_service import FileIOService
from app.core.services.report_generation.factories.report_generator_factory import (
    ReportGeneratorFactory,
)
from app.core.services.report_generation.base.report_generator import ReportGenerator
from app.core.utils.logging_setup import get_logger


class CoreFacade(object):
    __slots__ = (
        "_config",
        "_data_repository",
        "_file_io_service",
        "_logger",
    )

    def __init__(self, config: AppConfig) -> None:
        self._logger: Logger = get_logger(__name__)
        self._logger.debug("Initializing ApplicationFacade")

        # Dependency injection
        self._config: AppConfig = config
        self._data_repository: DuckDBRepository = DuckDBRepository(
            self._config.database_config
        )
        self._file_io_service: FileIOService = FileIOService(
            self._config.file_io_config
        )

        self._logger.info("ApplicationFacade initialized successfully")

    def generate_report(
        self,
        report_name: str,
        source_file_paths: dict[str, Path],
        output_directory_path: Path,
        report_context: ReportContext,
    ) -> Path:
        self._logger.info(f"Starting report generation: {report_name}")

        try:
            report_specification: ReportSpecification = ReportSpecificationRegistry.get(
                report_name
            )
            self._logger.info(f"Generating report: {report_specification.display_name}")
            self._logger.debug(f"Report category: {report_specification.category}")

            # Create generator and generate report
            generator: ReportGenerator = ReportGeneratorFactory.create_generator(
                report_name,
                self._file_io_service,
                self._data_repository,
                report_context,
            )
            self._logger.debug(f"Generator created: {generator.__class__.__name__}")

            self._logger.info("Starting report generation process")
            output_file_path: Path = generator.generate(
                source_file_paths=source_file_paths,
                output_directory_path=output_directory_path,
            )

            self._logger.info(f"Report generated successfully: {output_file_path}")
            print(f"Report generated successfully: {output_file_path}")

            return output_file_path

        except ValueError as e:
            self._logger.error(f"Configuration error: {e}")
            raise
        except Exception as e:
            self._logger.exception(f"Unexpected error during report generation: {e}")
            raise

    def get_available_reports(self) -> dict[str, ReportSpecification]:
        self._logger.debug("Retrieving available reports")
        reports: dict[str, ReportSpecification] = ReportSpecificationRegistry.all()
        self._logger.info(f"Found {len(reports)} available report types")
        return reports
