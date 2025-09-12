from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import Any

# Third-party imports
from pydantic import BaseModel, Field


class GUIState(BaseModel):
    selected_files: list[Path] = Field(default_factory=list[Path])
    selected_report: str | None = Field(default=None)
    output_path: Path | None = Field(default=None)
    available_reports: dict[str, Any] = Field(default_factory=dict[str, Any])

    model_config = {
        "arbitrary_types_allowed": True,
        "validate_assignment": True,
    }
