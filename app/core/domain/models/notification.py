from __future__ import annotations

# Standard library imports
from typing import Annotated

# Third-party imports
from pydantic import BaseModel, Field


class Notification(BaseModel):
    name: Annotated[
        str,
        Field(
            description="Notification name to be displayed",
        ),
    ]

    database_aliases: Annotated[
        list[str],
        Field(
            description="All the possible names of the same notification inside the database",
        ),
    ]

    aid_count: Annotated[
        int,
        Field(
            default=0,
            description="Total number of housing units planned in this notification",
            ge=0,
        ),
    ]

    aid_amount: Annotated[
        int,
        Field(
            default=0,
            description="Value of the financial aid provided (in dinars)",
            ge=0,
        ),
    ]

    model_config = {
        "frozen": True,
        "validate_assignment": True,
    }
