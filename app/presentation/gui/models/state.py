# Standard library imports
from pathlib import Path
from typing import Any, Optional, List, Dict

# Third-party imports
from pydantic import BaseModel, Field


class State(BaseModel):
    selected_files: List[Path] = Field(default_factory=list)
    selected_report: Optional[str] = Field(default=None)
    output_path: Optional[Path] = Field(default=None)
    available_reports: Dict[str, Any] = Field(default_factory=dict)

    model_config = {
        "arbitrary_types_allowed": True,
        "validate_assignment": True,
    }
