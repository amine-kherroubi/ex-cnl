# Standard library imports
from logging import Logger
from pathlib import Path
from typing import Any, Dict, List

# Local application imports
from app.common.logging_setup import get_logger
from app.config import AppConfig
from app.core.domain.enums.space_time import Month, Wilaya
from app.core.domain.models.report_context import ReportContext
from app.core.domain.models.report_specification import ReportSpecification
from app.core.domain.registries.report_specification_registry import (
    ReportSpecificationRegistry,
)
from app.core.domain.registries.subprogram_registry import SubprogramRegistry
from app.core.infrastructure.data.data_repository import DuckDBRepository
from app.core.infrastructure.file_io.file_io_service import FileIOService
from app.core.services.report_generation_service.base_report_generator import (
    BaseGenerator,
)
from app.core.services.report_generation_service.report_generator_factory import (
    ReportGeneratorFactory,
)
from app.core.services.file_validation_service import FileValidator


class CoreFacade(object):
    __slots__ = (
        "_config",
        "_data_repository",
        "_file_io_service",
        "_logger",
    )

    def __init__(self, config: AppConfig) -> None:
        self._logger: Logger = get_logger(__name__)
        self._logger.debug("Initializing application core facade")

        self._config: AppConfig = config
        self._data_repository: DuckDBRepository = DuckDBRepository(
            self._config.database_config
        )
        self._file_io_service: FileIOService = FileIOService(
            self._config.file_io_config
        )

        SubprogramRegistry.initialize(self._file_io_service)

        self._logger.info("CoreFacade initialized successfully")

    def get_available_reports(self) -> Dict[str, ReportSpecification]:
        self._logger.debug("Retrieving available reports from registry")

        try:
            reports: Dict[str, ReportSpecification] = ReportSpecificationRegistry.all()
            self._logger.info(f"Retrieved {len(reports)} available report types")
            return reports
        except Exception as e:
            self._logger.exception(f"Failed to retrieve available reports: {e}")
            raise

    def generate_report(
        self,
        report_name: str,
        source_files: List[Path],
        output_directory_path: Path,
        month: Month,
        year: int,
        **kwargs: Any,
    ) -> Path:
        self._logger.info(f"Starting report generation: {report_name}")
        self._logger.debug(f"Source files: {[str(f) for f in source_files]}")
        self._logger.debug(f"Output directory: {output_directory_path}")
        self._logger.debug(f"Period: {month.value} {year}")

        self._log_additional_parameters(kwargs)
        self._verify_report_exists(report_name)

        try:
            # Validate source files
            validation_result: Dict[str, Any] = FileValidator.validate(
                report_name, source_files
            )
            validated_files: Dict[str, Path] = validation_result["matched_files"]
            unmatched_files: List[Path] = validation_result["unmatched_files"]

            self._log_validation_results(validated_files, unmatched_files)

            # Create report context
            report_context: ReportContext = self._create_report_context(month, year)

            # Generate report
            output_file_path: Path = self._execute_report_generation(
                report_name,
                validated_files,
                output_directory_path,
                report_context,
                kwargs,
            )

            self._logger.info(
                f"Report generation completed successfully: {output_file_path}"
            )
            print(f"Report generated successfully: {output_file_path}")

            return output_file_path

        except (ValueError, FileNotFoundError) as e:
            self._logger.error(f"Report generation failed due to validation error: {e}")
            raise
        except Exception as e:
            self._logger.exception(f"Unexpected error during report generation: {e}")
            raise

    def _log_additional_parameters(self, kwargs: Dict[str, Any]) -> None:
        if kwargs:
            self._logger.debug(f"Additional parameters: {kwargs}")

        if "target_subprogram" in kwargs:
            self._logger.info(f"Target subprogram: {kwargs['target_subprogram']}")

        if "target_notification" in kwargs:
            self._logger.info(f"Target notification: {kwargs['target_notification']}")

    def _verify_report_exists(self, report_name: str) -> None:
        available_reports: Dict[str, ReportSpecification] = self.get_available_reports()

        if report_name not in available_reports:
            error_msg: str = f"Unknown report type: {report_name}"
            self._logger.error(error_msg)
            raise ValueError(error_msg)

    def _log_validation_results(
        self, validated_files: Dict[str, Path], unmatched_files: List[Path]
    ) -> None:
        self._logger.info(
            f"File validation successful. Validated {len(validated_files)} files"
        )

        if unmatched_files:
            warning_msg: str = (
                f"{len(unmatched_files)} files did not match any pattern and will be "
                f"ignored: {', '.join(f.name for f in unmatched_files)}"
            )
            self._logger.warning(warning_msg)

    def _create_report_context(self, month: Month, year: int) -> ReportContext:
        report_context: ReportContext = ReportContext(
            wilaya=Wilaya.TIZI_OUZOU,
            year=year,
            month=month,
        )

        self._logger.debug(
            f"Report context created: {report_context.wilaya.value}, "
            f"Period: {month} {year}, Report date: {report_context.reporting_date}"
        )

        return report_context

    def _execute_report_generation(
        self,
        report_name: str,
        validated_files: Dict[str, Path],
        output_directory_path: Path,
        report_context: ReportContext,
        kwargs: Dict[str, Any],
    ) -> Path:
        report_specification: ReportSpecification = ReportSpecificationRegistry.get(
            report_name
        )

        self._logger.info(f"Generating report: {report_specification.display_name}")
        self._logger.debug(f"Report category: {report_specification.category.value}")

        generator: BaseGenerator = ReportGeneratorFactory.create_generator(
            report_name=report_name,
            file_io_service=self._file_io_service,
            data_repository=self._data_repository,
            report_context=report_context,
            **kwargs,
        )

        self._logger.debug(f"Generator created: {generator.__class__.__name__}")
        self._logger.info("Starting report generation process")

        output_file_path: Path = generator.generate(
            source_file_paths=validated_files,
            output_directory_path=output_directory_path,
        )

        return output_file_path
