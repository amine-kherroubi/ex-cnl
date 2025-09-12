from __future__ import annotations

# Standard library imports
from typing import Annotated

# Third-party imports
from pydantic import BaseModel, Field


class Programme(BaseModel):
    name: Annotated[
        str,
        Field(
            description="Name of the programme.",
            min_length=1,
        ),
    ]

    year_start: Annotated[
        int,
        Field(description="Start year of the programme."),
    ]

    year_end: Annotated[
        int | None,
        Field(default=None, description="End year of the programme, if applicable."),
    ]

    display_order: Annotated[
        int,
        Field(default=0, description="Order in which the programme is displayed."),
    ]

    consistance: Annotated[
        int,
        Field(
            default=0,
            description="Total number of housing units planned for this programme.",
        ),
    ]

    model_config = {
        "frozen": True,
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }
