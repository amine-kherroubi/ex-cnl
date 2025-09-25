from __future__ import annotations

# Standard library imports
from typing import Annotated

# Third-party imports
from pydantic import BaseModel, Field


class Notification(BaseModel):
    names: Annotated[
        list[str],
        Field(
            description="Official programme name for housing projects",
        ),
    ]

    model_config = {
        "frozen": True,
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }
