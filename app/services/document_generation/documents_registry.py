from __future__ import annotations

# Standard library imports
from enum import StrEnum
from typing import Annotated, Final, final

# Third-party imports
from pydantic import BaseModel, Field

# Local application imports
from app.services.document_generation.generator_template import DocumentGenerator
from app.services.document_generation.concrete_generators.activite_mensuelle_hr import (
    ActiviteMensuelleHRGenerator,
)
from app.services.document_generation.concrete_generators.situation_des_programmes_hr import (
    SituationDesProgrammesHRGenerator,
)
from app.utils.space_time import Periodicity


class DocumentCategory(StrEnum):
    HR = "HR"


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
        "frozen": True,  # makes the model immutable
        "str_strip_whitespace": True,  # trims whitespace in str fields
        "validate_assignment": True,  # validate on assignment
    }


@final
class DocumentRegistry(object):  # Registry pattern
    __slots__ = ()

    def __init__(self):
        raise TypeError(f"{self.__class__.__name__} is not meant to be instantiated")

    @classmethod
    def get(cls, document_name: str) -> DocumentSpecification:
        if document_name not in cls._DOCUMENTS_DEFINITIONS:
            available = list(cls._DOCUMENTS_DEFINITIONS.keys())
            raise ValueError(
                f"Document '{document_name}' not found. Available: {available}"
            )
        return cls._DOCUMENTS_DEFINITIONS[document_name]

    @classmethod
    def has(cls, document_name: str) -> bool:
        return document_name in cls._DOCUMENTS_DEFINITIONS

    @classmethod
    def all(cls) -> dict[str, DocumentSpecification]:
        return cls._DOCUMENTS_DEFINITIONS.copy()

    _DOCUMENTS_DEFINITIONS: Final[dict[str, DocumentSpecification]] = {
        "activite_mensuelle_par_programme": DocumentSpecification(
            name="activite_mensuelle_par_programme",
            display_name="Activité mensuelle",
            category=DocumentCategory.HR,
            periodicity=Periodicity.MONTHLY,
            description=(
                "Document de suivi mensuel des activités par programme, "
                "renseigné par la BNH (ex-CNL)"
            ),
            required_files={
                r"^Journal_décisions__Agence_[A-Z+]+_\d{2}\.\d{2}\.\d{4}_[0-9]+.xlsx$": "décisions",
                r"^Journal_paiements__Agence_[A-Z+]+_\d{2}\.\d{2}\.\d{4}_[0-9]+.xlsx$": "paiements",
            },
            queries={},
            output_filename="Activité_mensuelle_par_programme_{wilaya}_{date}.xlsx",
            generator=ActiviteMensuelleHRGenerator,
        ),
        "situation_des_programmes": DocumentSpecification(
            name="situation_des_programmes",
            display_name="Situation des programmes",
            category=DocumentCategory.HR,
            periodicity=Periodicity.MONTHLY,
            description=(
                "Document de suivi de la situation des programmes, "
                "renseigné par la BNH (ex-CNL)"
            ),
            required_files={
                r"^Journal_décisions__Agence_[A-Z+]+_\d{2}\.\d{2}\.\d{4}_[0-9]+.xlsx$": "décisions",
                r"^Journal_paiements__Agence_[A-Z+]+_\d{2}\.\d{2}\.\d{4}_[0-9]+.xlsx$": "paiements",
            },
            queries={},
            output_filename="Situation_des_programmes_{wilaya}_{date}.xlsx",
            generator=SituationDesProgrammesHRGenerator,
        ),
    }

    PROGRAMMES_HABITAT_RURAL: list[str] = [
        'PEC "31/12/2004"',
        "QUINQU 2005-2009",
        "H PLATEAUX",
        "SUD",
        "RATTRAPAGE",
        "PRESIDENT",
        "COMPLEMENT",
        "PROG 2008",
        "PROG 2009",
        "SINISTRES",
        "QUINQU 2010-2014",
        "COMPL 2010-2014",
        "QUINQU 2015-2019",
        "TR 2016",
        "INCENDIES 2017",
        "QUINQU 2016",
        "QUINQU 2018",
        "QUINQU 2019",
        "QUINQU 2020",
    ]

    TRANCHES_LANCEMENT: set[str] = {
        "20%  1 ERE TRANCHE",
        "60%  Première Tranche",
        "40%  Première Tranche",
        "60%  1+2 EME TRANCHE",
        "100%  Tranche totale",
        "100%  1+2+3 EME TRANCHE",
    }

    TRANCHES_LIVRAISON: set[str] = {
        "40%  3 EME TRANCHE",
        "40%  Deuxième Tranche",
        "80%  2+3 EME TRANCHE",
        "40%  C2",
        "60%  Deuxième Tranche",
        "Tranche complémentaire 2",
        "100%  Tranche totale",
        "100%  1+2+3 EME TRANCHE",
        "40%  2 EME TRANCHE",
    }
