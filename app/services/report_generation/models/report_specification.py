from __future__ import annotations

# Standard library imports
from typing import Annotated

# Third-party imports
from pydantic import BaseModel, Field

# Local application imports
from app.services.report_generation.report_generator_template import (
    ReportGenerator,
)
from app.services.report_generation.enums.report_category import ReportCategory
from app.services.report_generation.enums.space_time import Periodicity


class ReportSpecification(BaseModel):
    name: Annotated[
        str,
        Field(
            description="Unique internal report name",
            min_length=1,
        ),
    ]

    display_name: Annotated[
        str,
        Field(
            description="User-friendly report name for display",
            min_length=1,
        ),
    ]

    category: Annotated[
        ReportCategory,
        Field(description="Thematic category of the report"),
    ]

    periodicity: Annotated[
        Periodicity, Field(description="Report generation frequency")
    ]

    description: Annotated[
        str,
        Field(description="Detailed description of report purpose"),
    ]

    required_files: Annotated[
        dict[str, str],
        Field(
            description="Mapping of regex filename patterns to corresponding SQL view names"
        ),
    ]

    queries: Annotated[
        dict[str, str],
        Field(description="Mapping of query names to corresponding SQL templates"),
    ]

    output_filename: Annotated[
        str,
        Field(description="Template for output Excel filename generation"),
    ]

    generator: Annotated[
        type[ReportGenerator],
        Field(description="Concrete generator class responsible for report production"),
    ]

    model_config = {
        "frozen": True,
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }
