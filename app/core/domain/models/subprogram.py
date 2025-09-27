from __future__ import annotations

# Standard library imports
from typing import Annotated

# Third-party imports
from pydantic import BaseModel, Field

from app.core.domain.models.notification import Notification


class Subprogram(BaseModel):
    name: Annotated[
        str,
        Field(
            description="Subprogram name to be displayed",
            min_length=1,
        ),
    ]

    database_alias: Annotated[
        str,
        Field(
            description="Exact subprogram name inside the database",
            min_length=1,
        ),
    ]

    notifications: Annotated[
        list[Notification],
        Field(
            description="Notifications of this subprogram",
        ),
    ]

    model_config = {
        "frozen": True,
        "validate_assignment": True,
    }
