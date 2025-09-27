# Standard library imports
from typing import List

# Third-party imports
from pydantic import BaseModel, Field


class Notification(BaseModel):
    name: str = Field(
        description="Notification name to be displayed",
    )

    database_aliases: List[str] = Field(
        description="All the possible names of the same notification inside the database",
    )

    aid_count: int = Field(
        default=0,
        description="Total number of housing units planned in this notification",
        ge=0,
    )

    aid_amount: int = Field(
        default=0,
        description="Value of the financial aid provided (in dinars)",
        ge=0,
    )

    class Config:
        frozen = True
        validate_assignment = True
