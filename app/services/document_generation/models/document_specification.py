from __future__ import annotations

# Standard library imports
from typing import Annotated

# Third-party imports
from pydantic import BaseModel, Field

# Local application imports
from app.services.document_generation.document_generator_template import (
    DocumentGenerator,
)
from app.services.document_generation.enums.document_category import DocumentCategory
from app.services.document_generation.enums.space_time import Periodicity


class DocumentSpecification(BaseModel):
    name: Annotated[
        str,
        Field(
            description="Unique internal name of the document",
            min_length=1,
        ),
    ]

    display_name: Annotated[
        str, Field(description="Human-readable name of the document.", min_length=1)
    ]

    category: Annotated[
        DocumentCategory,
        Field(description="Category of the document."),
    ]

    periodicity: Annotated[
        Periodicity, Field(description="How often this document is generated.")
    ]

    description: Annotated[
        str,
        Field(description="Detailed description of the document purpose."),
    ]

    required_files: Annotated[
        dict[str, str],
        Field(
            description="Mapping of regex filename patterns to view names that must be present for this document."
        ),
    ]

    queries: Annotated[
        dict[str, str],
        Field(description="Mapping of query names to SQL queries."),
    ]

    output_filename: Annotated[
        str,
        Field(description="The Excel filename to generate as output."),
    ]

    generator: Annotated[
        type[DocumentGenerator],
        Field(
            description="Concrete generator class responsible for producing the document."
        ),
    ]

    model_config = {
        "frozen": True,
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }
