# Standard library imports
from typing import Type, Dict, List

# Third-party imports
from pydantic import BaseModel, Field

# Local application imports
from app.core.domain.enums.report_category import ReportCategory
from app.core.domain.models.required_file import RequiredFile
from app.core.services.report_generation_service.base_report_generator import (
    BaseGenerator,
)


class ReportSpecification(BaseModel):
    name: str = Field(
        description="Unique internal report name",
        min_length=1,
    )

    display_name: str = Field(
        description="User-friendly report name for display",
        min_length=1,
    )

    category: ReportCategory = Field(
        description="Thematic category of the report",
    )

    description: str = Field(
        description="Detailed description of report purpose",
    )

    required_files: List[RequiredFile] = Field(
        description=(
            "Mapping of file names keys to required file specifications "
            "(pattern, readable pattern, associated database table)"
        ),
    )

    output_filename: str = Field(
        description="Template for output Excel filename generation",
    )

    generator: Type[BaseGenerator] = Field(
        description="Concrete generator class responsible for report production",
    )

    queries: Dict[str, str] = Field(
        description="Mapping of query names to corresponding SQL templates",
    )

    class Config:
        frozen = True
        validate_assignment = True
