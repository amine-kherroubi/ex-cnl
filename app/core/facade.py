from __future__ import annotations

# Standard library imports
import re
from logging import Logger
from pathlib import Path
from typing import Any

# Local application imports
from app.config import AppConfig
from app.core.domain.enums.space_time import Month, Wilaya
from app.core.domain.models.report_context import ReportContext
from app.core.domain.models.report_specification import (
    ReportSpecification,
    RequiredFile,
)
from app.core.domain.registries.report_specification_registry import (
    ReportSpecificationRegistry,
)
from app.core.domain.registries.subprogram_registry import SubprogramRegistry
from app.core.infrastructure.data.data_repository import DuckDBRepository
from app.core.infrastructure.file_io.file_io_service import FileIOService
from app.core.services.report_generation_service.factories.report_generator_factory import (
    ReportGeneratorFactory,
)
from app.core.services.report_generation_service.base_generator import BaseGenerator
from app.common.logging_setup import get_logger


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

    def get_available_reports(self) -> dict[str, ReportSpecification]:
        self._logger.debug("Retrieving available reports from registry")

        try:
            reports: dict[str, ReportSpecification] = ReportSpecificationRegistry.all()
            self._logger.info(f"Retrieved {len(reports)} available report types")
            return reports
        except Exception as e:
            self._logger.exception(f"Failed to retrieve available reports: {e}")
            raise

    def generate_report(
        self,
        report_name: str,
        source_files: list[Path],
        output_directory_path: Path,
        month: Month,
        year: int,
        **kwargs: Any,
    ) -> Path:
        self._logger.info(f"Starting report generation: {report_name}")
        self._logger.debug(f"Source files: {[str(f) for f in source_files]}")
        self._logger.debug(f"Output directory: {output_directory_path}")
        self._logger.debug(f"Period: {month} {year}")
        self._logger.debug(f"Additional parameters: {kwargs}")

        if "target_subprogram" in kwargs:
            self._logger.info(f"Target subprogram: {kwargs['target_subprogram']}")
        if "target_notification" in kwargs:
            self._logger.info(f"Target notification: {kwargs['target_notification']}")

        try:
            self._logger.debug("Validating source files against report requirements")
            validated_files: dict[str, Path] = self._validate_source_files(
                report_name, source_files
            )
            self._logger.info(
                f"File validation successful. Validated {len(validated_files)} files"
            )

            self._logger.debug("Delegating report generation to facade")

            report_context: ReportContext = ReportContext(
                wilaya=Wilaya.TIZI_OUZOU,
                year=year,
                month=month,
            )

            self._logger.debug(
                f"Report context created: {report_context.wilaya.value}, "
                f"Period: {month} {year}, Report date: {report_context.reporting_date}"
            )

            report_specification: ReportSpecification = ReportSpecificationRegistry.get(
                report_name
            )
            self._logger.info(f"Generating report: {report_specification.display_name}")
            self._logger.debug(f"Report category: {report_specification.category}")

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

            self._logger.info(
                f"Report generation completed successfully: {output_file_path}"
            )
            self._logger.info(f"Report generated successfully: {output_file_path}")
            print(f"Report generated successfully: {output_file_path}")

            return output_file_path

        except (ValueError, FileNotFoundError) as e:
            self._logger.error(f"Report generation failed due to validation error: {e}")
            raise
        except Exception as e:
            self._logger.exception(f"Unexpected error during report generation: {e}")
            raise

    def _validate_source_files(
        self, report_name: str, input_files: list[Path]
    ) -> dict[str, Path]:
        self._logger.debug(
            f"Validating {len(input_files)} source files for report: {report_name}"
        )

        available_reports: dict[str, ReportSpecification] = self.get_available_reports()

        if report_name not in available_reports:
            error_msg: str = f"Unknown report type: {report_name}"
            self._logger.error(error_msg)
            raise ValueError(error_msg)

        report_spec: ReportSpecification = available_reports[report_name]
        required_files: list[RequiredFile] = report_spec.required_files
        self._logger.debug(
            f"Report requires {len(required_files)} files: "
            f"{[(rf.name, rf.readable_pattern) for rf in required_files]}"
        )

        self._logger.debug("Checking if all input files exist")
        for file_path in input_files:
            if not file_path.exists():
                error_msg: str = f"File does not exist: {file_path}"
                self._logger.error(error_msg)
                raise FileNotFoundError(error_msg)
        self._logger.debug("All input files exist")

        self._logger.debug("Matching files to required patterns")
        matched_files: dict[str, Path] = {}
        unmatched_files: list[Path] = []

        for file_path in input_files:
            file_matched: bool = False
            self._logger.debug(f"Checking file: {file_path.name}")

            for rf in required_files:
                if re.match(rf.pattern, file_path.name, re.IGNORECASE):
                    matched_files[rf.table_name] = file_path
                    file_matched = True
                    self._logger.debug(
                        f"File '{file_path.name}' matched pattern '{rf.readable_pattern}' "
                        f"-> table '{rf.table_name}'"
                    )
                    break

            if not file_matched:
                unmatched_files.append(file_path)
                self._logger.warning(
                    f"File '{file_path.name}' did not match any required pattern"
                )

        self._logger.debug("Checking if all required files are satisfied")
        missing_files: list[str] = []
        for rf in required_files:
            if rf.table_name not in matched_files:
                missing_files.append(
                    f"Pattern: '{rf.readable_pattern}' -> Table: '{rf.table_name}'"
                )
                self._logger.error(
                    f"Missing file for required pattern: '{rf.readable_pattern}' -> '{rf.table_name}'"
                )

        if missing_files:
            error_msg: str = "Missing files for required patterns:\n" + "\n".join(
                missing_files
            )
            self._logger.error("Validation failed: missing required patterns")
            raise ValueError(error_msg)

        if unmatched_files:
            error_msg: str = (
                "The following files don't match any required pattern:\n"
                + "\n".join(str(f) for f in unmatched_files)
            )
            self._logger.error(
                f"Validation failed: {len(unmatched_files)} unmatched files"
            )
            raise ValueError(error_msg)

        self._logger.info(
            f"File validation successful: {len(matched_files)} files matched to required patterns"
        )
        return matched_files
