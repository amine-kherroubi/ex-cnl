from __future__ import annotations

# Standard library imports
from typing import Annotated

# Third-party imports
from pydantic import BaseModel, Field


class Programme(BaseModel):
    name: Annotated[
        str,
        Field(
            description="Official program name for housing projects",
            min_length=1,
        ),
    ]

    year_start: Annotated[
        int,
        Field(description="Program starting year"),
    ]

    year_end: Annotated[
        int | None,
        Field(
            default=None,
            description="Program ending year, None if program is ongoing",
        ),
    ]

    display_order: Annotated[
        int,
        Field(
            default=0,
            description="Display order of program in reports and tables",
        ),
    ]

    consistance: Annotated[
        int,
        Field(
            default=0,
            description="Total number of housing units planned in this program",
            ge=0,
        ),
    ]

    model_config = {
        "frozen": True,
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }
