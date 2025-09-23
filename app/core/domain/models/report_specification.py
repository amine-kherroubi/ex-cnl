from __future__ import annotations

# Standard library imports
from typing import Annotated

# Third-party imports
from pydantic import BaseModel, Field

# Local application imports
from app.core.domain.enums.report_category import ReportCategory
from app.core.services.report_generation.base.report_generator import (
    ReportGenerator,
)


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

    description: Annotated[
        str,
        Field(description="Detailed description of report purpose"),
    ]

    required_files: Annotated[
        dict[str, RequiredFile],
        Field(
            description="Mapping of file names keys to required file specifications "
            "(pattern, readable pattern, associated database table)"
        ),
    ]

    output_filename: Annotated[
        str,
        Field(description="Template for output Excel filename generation"),
    ]

    generator: Annotated[
        type[ReportGenerator],
        Field(description="Concrete generator class responsible for report production"),
    ]

    queries: Annotated[
        dict[str, str],
        Field(description="Mapping of query names to corresponding SQL templates"),
    ]

    model_config = {
        "frozen": True,
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }


class RequiredFile(BaseModel):
    pattern: Annotated[
        str,
        Field(
            description="Regex pattern that filenames must match",
        ),
    ]
    readable_pattern: Annotated[
        str,
        Field(description="Readable pattern of a valid filename"),
    ]
    table: Annotated[
        str,
        Field(description="Associated SQL table name"),
    ]

    model_config = {
        "frozen": True,
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }
