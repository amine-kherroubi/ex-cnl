from __future__ import annotations

# Standard library imports
from typing import Annotated

# Third-party imports
from pydantic import BaseModel, Field


class RequiredFile(BaseModel):
    name: Annotated[
        str,
        Field(description="Name of the required file"),
    ]

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

    table_name: Annotated[
        str,
        Field(description="Associated SQL table name"),
    ]

    model_config = {
        "frozen": True,
        "validate_assignment": True,
    }
