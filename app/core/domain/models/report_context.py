# Standard library imports
from datetime import date

# Third-party imports
from pydantic import BaseModel, Field, validator

# Local application imports
from app.core.domain.enums.space_time import Wilaya, Month


class ReportContext(BaseModel):
    wilaya: Wilaya = Field(
        description="Algerian administrative division for this report",
    )

    year: int = Field(
        description="Year of the report period",
        ge=2000,
        le=2100,
    )

    reporting_date: date = Field(
        default_factory=date.today,
        description="Specific date for report generation",
    )

    month: Month = Field(
        default_factory=lambda: Month.from_number(date.today().month),
        description="Month of the report period in French (for monthly reports)",
    )

    @validator("reporting_date")
    def validate_report_date(cls, report_date: date) -> date:
        if report_date > date.today():
            raise ValueError("Report date cannot be in the future")
        return report_date

    class Config:
        frozen = True
        validate_assignment = True
