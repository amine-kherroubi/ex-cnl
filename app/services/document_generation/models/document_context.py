from __future__ import annotations

# Standard library imports
from datetime import date

# Third-party imports
from pydantic import BaseModel, Field, field_validator

# Local application imports
from app.services.document_generation.enums.space_time import Wilaya, Month


class DocumentContext(BaseModel):
    wilaya: Wilaya = Field(
        description="The Algerian wilaya (administrative division) for this document.",
    )

    year: int = Field(
        description="The year for the reporting period.",
        ge=2000,
        le=2100,
    )

    report_date: date = Field(
        description="The specific date when the report is generated or data is extracted.",
    )

    # Optional fields - only used when relevant
    month: Month | None = Field(
        default=None,
        description="The month for the reporting period in French.",
    )

    semester: int | None = Field(
        default=None,
        description="Semester (1 or 2) for semiannual reports.",
        ge=1,
        le=2,
    )

    @field_validator("report_date")
    @classmethod
    def validate_report_date(cls, report_date: date) -> date:
        if report_date > date.today():
            raise ValueError("Report date cannot be in the future")
        return report_date

    model_config = {
        "frozen": True,
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }
