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
        self, report_name: str, input_files: list[Path], output_directory: Path
    ) -> str:
        """
        Generate a report with validated input files.

        Args:
            report_name: Name of the report type to generate
            input_files: List of input file paths selected by the user
            output_directory: Directory where the output file should be saved

        Returns:
            Path to the generated output file
        """
        try:
            # Validate input files against report requirements
            validated_files: dict[str, Path] = self._validate_source_files(
                report_name, input_files
            )

            # Get report specification for output filename
            available_docs: dict[str, ReportSpecification] = (
                self._facade.get_available_reports()
            )
            report_spec: ReportSpecification = available_docs[report_name]

            # Create output file path
            output_filename: str = report_spec.output_filename
            if not output_filename.endswith(".xlsx"):
                output_filename += ".xlsx"
            output_file_path = output_directory / output_filename

            # Generate the report
            self._facade.generate_report(
                report_name=report_name,
                source_file_paths=validated_files,
                output_file_path=output_file_path,
            )

            return str(output_file_path)

        except Exception as e:
            raise e

    def _validate_source_files(
        self, report_name: str, input_files: list[Path]
    ) -> dict[str, Path]:
        """
        Validate input files against report requirements.

        Args:
            report_name: Name of the report type to generate
            input_files: List of file paths selected by the user

        Returns:
            Dictionary mapping view names to matching file paths

        Raises:
            ValueError: If validation fails or required patterns are not matched
        """
        # Get available reports to find the specification
        available_docs: dict[str, ReportSpecification] = (
            self._facade.get_available_reports()
        )

        if report_name not in available_docs:
            raise ValueError(f"Unknown report type: {report_name}")

        report_spec: ReportSpecification = available_docs[report_name]
        required_patterns = report_spec.required_files

        # Validate that all files exist
        missing_files: list[Path] = [f for f in input_files if not f.exists()]
        if missing_files:
            raise ValueError(f"The following files do not exist: {missing_files}")

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

        # Check if we have files for all required patterns
        missing_patterns: list[str] = []
        for pattern, view_name in required_patterns.items():
            if view_name not in matched_files:
                missing_patterns.append(f"Pattern: '{pattern}' -> View: '{view_name}'")

        # Report validation results
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
