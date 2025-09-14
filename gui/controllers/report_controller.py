from __future__ import annotations

# Standard library imports
import re
from pathlib import Path

# Local application imports
from app.application_facade import ApplicationFacade
from app.config import AppConfig
from app.services.report_generation.models.report_specification import (
    ReportSpecification,
)


class ReportController(object):
    __slots__ = "_facade"

    def __init__(self) -> None:
        self._facade: ApplicationFacade = ApplicationFacade(config=AppConfig())

    def get_available_reports(self) -> dict[str, ReportSpecification]:
        """Get all available report types from the facade."""
        return self._facade.get_available_reports()

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
        # Validate input files against report requirements (fail fast)
        validated_files: dict[str, Path] = self._validate_source_files(
            report_name, source_files
        )

        # Generate the report (facade will handle filename generation)
        output_file_path = self._facade.generate_report(
            report_name=report_name,
            source_file_paths=validated_files,
            output_directory_path=output_directory_path,
        )

        return output_file_path

    def _validate_source_files(
        self, report_name: str, input_files: list[Path]
    ) -> dict[str, Path]:
        """
        Validate input files against report requirements (fail fast).

        Args:
            report_name: Name of the report type to generate
            input_files: List of file paths selected by the user

        Returns:
            Dictionary mapping view names to matching file paths

        Raises:
            ValueError: If validation fails or required patterns are not matched
            FileNotFoundError: If files don't exist
        """
        # Get report specification
        available_reports: dict[str, ReportSpecification] = (
            self._facade.get_available_reports()
        )

        if report_name not in available_reports:
            raise ValueError(f"Unknown report type: {report_name}")

        report_spec: ReportSpecification = available_reports[report_name]
        required_patterns = report_spec.required_files

        # Validate that all files exist (fail fast)
        for file_path in input_files:
            if not file_path.exists():
                raise FileNotFoundError(f"File does not exist: {file_path}")

        # Match files to required patterns
        matched_files: dict[str, Path] = {}
        unmatched_files: list[Path] = []

        for file_path in input_files:
            file_matched = False

            for pattern, view_name in required_patterns.items():
                if re.match(pattern, file_path.name, re.IGNORECASE):
                    matched_files[view_name] = file_path
                    file_matched = True
                    break

            if not file_matched:
                unmatched_files.append(file_path)

        # Check if we have files for all required patterns (fail fast)
        missing_patterns: list[str] = []
        for pattern, view_name in required_patterns.items():
            if view_name not in matched_files:
                missing_patterns.append(f"Pattern: '{pattern}' -> View: '{view_name}'")

        # Report validation results (fail fast)
        if missing_patterns:
            raise ValueError(
                f"Missing files for required patterns:\n" + "\n".join(missing_patterns)
            )

        if unmatched_files:
            raise ValueError(
                f"The following files don't match any required pattern:\n"
                + "\n".join(str(f) for f in unmatched_files)
            )

        return matched_files
