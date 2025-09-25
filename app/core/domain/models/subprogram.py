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
            description="Official subprogram name for housing projects",
            min_length=1,
        ),
    ]

    display_order: Annotated[
        int,
        Field(
            description="Display order of subprogram in reports and tables",
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
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }
