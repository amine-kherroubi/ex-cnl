from __future__ import annotations

# Standard library imports
from typing import Annotated

# Third-party imports
from pydantic import BaseModel, Field


class Programme(BaseModel):
    name: Annotated[
        str,
        Field(
            description="Official programme name for housing projects",
            min_length=1,
        ),
    ]

    year_start: Annotated[
        int,
        Field(description="Programme starting year"),
    ]

    year_end: Annotated[
        int | None,
        Field(
            default=None,
            description="Programme ending year, None if programme is ongoing",
        ),
    ]

    display_order: Annotated[
        int,
        Field(
            default=0,
            description="Display order of programme in reports and tables",
        ),
    ]

    aid_count: Annotated[
        int,
        Field(
            default=0,
            description="Total number of housing units planned in this programme",
            ge=0,
        ),
    ]

    aid_value: Annotated[
        int,
        Field(
            default=0,
            description="Value of the financial aid provided (in dinars)",
            ge=0,
        ),
    ]

    model_config = {
        "frozen": True,
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }
