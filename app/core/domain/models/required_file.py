# Third-party imports
from pydantic import BaseModel, Field


class RequiredFile(BaseModel):
    name: str = Field(
        description="Name of the required file",
    )

    pattern: str = Field(
        description="Regex pattern that filenames must match",
    )

    readable_pattern: str = Field(
        description="Readable pattern of a valid filename",
    )

    table_name: str = Field(
        description="Associated SQL table name",
    )

    class Config:
        frozen = True
        validate_assignment = True
