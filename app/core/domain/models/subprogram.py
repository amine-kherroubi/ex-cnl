# Standard library imports
from typing import List

# Third-party imports
from pydantic import BaseModel, Field

from app.core.domain.models.notification import Notification


class Subprogram(BaseModel):
    name: str = Field(
        description="Subprogram name to be displayed",
        min_length=1,
    )

    database_alias: str = Field(
        description="Exact subprogram name inside the database",
        min_length=1,
    )

    notifications: List[Notification] = Field(
        description="Notifications of this subprogram",
    )

    class Config:
        frozen = True
        validate_assignment = True
