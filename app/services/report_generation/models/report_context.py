from __future__ import annotations

# Standard library imports
from datetime import date

# Third-party imports
from pydantic import BaseModel, Field, field_validator

# Local application imports
from app.services.report_generation.enums.space_time import Wilaya, Month


class ReportContext(BaseModel):
    wilaya: Wilaya = Field(
        description="Algerian administrative division for this report",
    )

    year: int = Field(
        description="Year of the report period",
        ge=2000,
        le=2100,
    )

    report_date: date = Field(
        description="Specific date for report generation or data extraction",
    )

    # Optional fields - used only according to context
    month: Month | None = Field(
        default=None,
        description="Month of the report period in French (for monthly reports)",
    )

    semester: int | None = Field(
        default=None,
        description="Semester (1 or 2) for semi-annual reports",
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
