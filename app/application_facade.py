from __future__ import annotations

# Standard library imports
from datetime import date
from logging import Logger
from pathlib import Path

# Local application imports
from app.services.report_generation.report_generator_template import (
    ReportGenerator,
)
from app.data.data_repository import DuckDBRepository
from app.services.report_generation.report_specification_registry import (
    ReportSpecificationRegistry,
)
from app.services.report_generation.report_specification_registry import (
    ReportSpecification,
)
from app.services.file_io.file_io_service import FileIOService
from app.services.report_generation.factories.report_context_factory import (
    ReportContextFactory,
)
from app.services.report_generation.models.report_context import (
    ReportContext,
)
from app.services.report_generation.enums.space_time import Wilaya
from app.config import AppConfig
from app.services.report_generation.factories.report_generator_factory import (
    ReportGeneratorFactory,
)
from app.utils.logging_setup import get_logger


class ApplicationFacade(object):  # Facade pattern
    __slots__ = (
        "_config",
        "_data_repository",
        "_file_io_service",
        "_logger",
    )

    def __init__(self, config: AppConfig) -> None:
        self._logger: Logger = get_logger(__name__)
        self._logger.debug("Initializing ApplicationFacade")

        # Dependency injection pattern
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
    ) -> Path:
        self._logger.info(f"Starting report generation: {report_name}")

        try:
            report_specification: ReportSpecification = ReportSpecificationRegistry.get(
                report_name
            )
            self._logger.info(f"Generating report: {report_specification.display_name}")
            self._logger.debug(f"Report category: {report_specification.category}")

            # Create report spatiotemporal context
            report_context: ReportContext = ReportContextFactory.create_context(
                wilaya=Wilaya.TIZI_OUZOU,
                periodicity=report_specification.periodicity,
                report_date=date(2025, 9, 6),
            )
            self._logger.debug(
                f"Report context created: {report_context.wilaya.value}, {report_context.report_date}"
            )

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
