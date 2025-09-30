# Standard library imports
import re
from logging import Logger
from pathlib import Path
from typing import Any, Dict, List, final

# Local application imports
from app.common.logging_setup import get_logger
from app.core.domain.models.report_specification import ReportSpecification
from app.core.domain.models.required_file import RequiredFile
from app.core.domain.registries.report_specification_registry import (
    ReportSpecificationRegistry,
)


@final
class FileValidator(object):
    __slots__ = ()
    
    _logger: Logger = get_logger(__name__)

    def __new__(cls) -> None:
        raise RuntimeError(
            f"{cls.__name__} is not intended to be instantiated. Use class methods."
        )

    @classmethod
    def validate(
        cls, report_name: str, input_files: List[Path]
    ) -> Dict[str, Any]:
        cls._logger.debug(
            f"Validating {len(input_files)} source files for report: {report_name}"
        )

        report_spec: ReportSpecification = ReportSpecificationRegistry.get(report_name)
        required_files: List[RequiredFile] = report_spec.required_files

        cls._logger.debug(
            f"Report requires {len(required_files)} files: "
            f"{[(rf.name, rf.readable_pattern) for rf in required_files]}"
        )

        cls._verify_files_exist(input_files)

        matched_files: Dict[str, Path] = {}
        unmatched_files: List[Path] = []

        cls._match_files_to_patterns(
            input_files, required_files, matched_files, unmatched_files
        )

        cls._verify_required_patterns_satisfied(required_files, matched_files)

        cls._logger.info(
            f"File validation successful: {len(matched_files)} files matched to required patterns"
        )

        if unmatched_files:
            cls._logger.info(f"{len(unmatched_files)} unmatched files will be ignored")

        return {
            "matched_files": matched_files,
            "unmatched_files": unmatched_files,
        }

    @classmethod
    def _verify_files_exist(cls, input_files: List[Path]) -> None:
        cls._logger.debug("Checking if all input files exist")

        for file_path in input_files:
            if not file_path.exists():
                error_msg: str = f"File does not exist: {file_path}"
                cls._logger.error(error_msg)
                raise FileNotFoundError(error_msg)

        cls._logger.debug("All input files exist")

    @classmethod
    def _match_files_to_patterns(
        cls,
        input_files: List[Path],
        required_files: List[RequiredFile],
        matched_files: Dict[str, Path],
        unmatched_files: List[Path],
    ) -> None:
        cls._logger.debug("Matching files to required patterns")

        for file_path in input_files:
            file_matched: bool = False
            cls._logger.debug(f"Checking file: {file_path.name}")

            for rf in required_files:
                if re.match(rf.pattern, file_path.name, re.IGNORECASE):
                    matched_files[rf.table_name] = file_path
                    file_matched = True
                    cls._logger.debug(
                        f"File '{file_path.name}' matched pattern '{rf.readable_pattern}' "
                        f"-> table '{rf.table_name}'"
                    )
                    break

            if not file_matched:
                unmatched_files.append(file_path)
                cls._logger.warning(
                    f"File '{file_path.name}' did not match any required pattern and will be ignored"
                )

    @classmethod
    def _verify_required_patterns_satisfied(
        cls, required_files: List[RequiredFile], matched_files: Dict[str, Path]
    ) -> None:
        cls._logger.debug("Checking if all required files are satisfied")

        missing_files: List[str] = []

        for rf in required_files:
            if rf.table_name not in matched_files:
                missing_files.append(
                    f"Pattern: '{rf.readable_pattern}' -> Table: '{rf.table_name}'"
                )
                cls._logger.error(
                    f"Missing file for required pattern: '{rf.readable_pattern}' -> '{rf.table_name}'"
                )

        if missing_files:
            error_msg: str = "Missing files for required patterns:\n" + "\n".join(
                missing_files
            )
            cls._logger.error("Validation failed: missing required patterns")
            raise ValueError(error_msg)