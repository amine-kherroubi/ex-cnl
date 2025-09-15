from __future__ import annotations

# Standard library imports
import re
from logging import Logger
from pathlib import Path

# Local application imports
from app.application_facade import ApplicationFacade
from app.services.report_generation.models.report_specification import (
    ReportSpecification,
)
from app.utils.logging_setup import get_logger


class ReportController(object):
    __slots__ = ("_facade", "_logger")

    def __init__(self, facade: ApplicationFacade) -> None:
        self._logger: Logger = get_logger("gui.controllers.report_controller")
        self._logger.debug("Initializing ReportController with injected facade")

        self._facade: ApplicationFacade = facade
        self._logger.info("ReportController initialized successfully")

    def get_available_reports(self) -> dict[str, ReportSpecification]:
        """Get all available report types from the facade."""
        self._logger.debug("Retrieving available reports from facade")

        try:
            reports = self._facade.get_available_reports()
            self._logger.info(f"Retrieved {len(reports)} available report types")
            return reports
        except Exception as e:
            self._logger.exception(f"Failed to retrieve available reports: {e}")
            raise

    def generate_report(
        self, report_name: str, source_files: list[Path], output_directory_path: Path
    ) -> Path:
        """
        Generate a report with validated input files.

        Args:
            report_name: Name of the report type to generate
            source_files: List of input file paths selected by the user
            output_directory_path: Directory where the output file should be saved

        Returns:
            Path to the generated output file

        Raises:
            ValueError: If validation fails or report configuration is invalid
            FileNotFoundError: If required files don't exist
        """
        self._logger.info(f"Starting report generation: {report_name}")
        self._logger.debug(f"Source files: {[str(f) for f in source_files]}")
        self._logger.debug(f"Output directory: {output_directory_path}")

        try:
            # Validate input files against report requirements (fail fast)
            self._logger.debug("Validating source files against report requirements")
            validated_files: dict[str, Path] = self._validate_source_files(
                report_name, source_files
            )
            self._logger.info(
                f"File validation successful. Validated {len(validated_files)} files"
            )

            # Generate the report (facade will handle filename generation)
            self._logger.debug("Delegating report generation to facade")
            output_file_path: Path = self._facade.generate_report(
                report_name=report_name,
                source_file_paths=validated_files,
                output_directory_path=output_directory_path,
            )

            self._logger.info(
                f"Report generation completed successfully: {output_file_path}"
            )
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
        """
        Validate input files against report requirements (fail fast).

        Args:
            report_name: Name of the report type to generate
            input_files: List of file paths selected by the user

        Returns:
            Dictionary mapping table names to matching file paths

        Raises:
            ValueError: If validation fails or required patterns are not matched
            FileNotFoundError: If files don't exist
        """
        self._logger.debug(
            f"Validating {len(input_files)} source files for report: {report_name}"
        )

        # Get report specification
        available_reports: dict[str, ReportSpecification] = (
            self._facade.get_available_reports()
        )

        if report_name not in available_reports:
            error_msg = f"Unknown report type: {report_name}"
            self._logger.error(error_msg)
            raise ValueError(error_msg)

        report_spec: ReportSpecification = available_reports[report_name]
        required_patterns = report_spec.required_files
        self._logger.debug(
            f"Report requires {len(required_patterns)} file patterns: {list(required_patterns.keys())}"
        )

        # Validate that all files exist (fail fast)
        self._logger.debug("Checking if all input files exist")
        for file_path in input_files:
            if not file_path.exists():
                error_msg = f"File does not exist: {file_path}"
                self._logger.error(error_msg)
                raise FileNotFoundError(error_msg)

        self._logger.debug("All input files exist")

        # Match files to required patterns
        self._logger.debug("Matching files to required patterns")
        matched_files: dict[str, Path] = {}
        unmatched_files: list[Path] = []

        for file_path in input_files:
            file_matched = False
            self._logger.debug(f"Checking file: {file_path.name}")

            for pattern, table_name in required_patterns.items():
                if re.match(pattern, file_path.name, re.IGNORECASE):
                    matched_files[table_name] = file_path
                    file_matched = True
                    self._logger.debug(
                        f"File '{file_path.name}' matched pattern '{pattern}' -> table '{table_name}'"
                    )
                    break

            if not file_matched:
                unmatched_files.append(file_path)
                self._logger.warning(
                    f"File '{file_path.name}' did not match any required pattern"
                )

        # Check if we have files for all required patterns (fail fast)
        self._logger.debug("Checking if all required patterns are satisfied")
        missing_patterns: list[str] = []
        for pattern, table_name in required_patterns.items():
            if table_name not in matched_files:
                missing_patterns.append(
                    f"Pattern: '{pattern}' -> Table: '{table_name}'"
                )
                self._logger.error(
                    f"Missing file for required pattern: '{pattern}' -> '{table_name}'"
                )

        # Report validation results (fail fast)
        if missing_patterns:
            error_msg = f"Missing files for required patterns:\n" + "\n".join(
                missing_patterns
            )
            self._logger.error(f"Validation failed: missing required patterns")
            raise ValueError(error_msg)

        if unmatched_files:
            error_msg = (
                f"The following files don't match any required pattern:\n"
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
