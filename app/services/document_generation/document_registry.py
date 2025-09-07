from __future__ import annotations

# Standard library imports
from typing import Final, final

# Local application imports
from app.services.document_generation.concrete_generators.activite_mensuelle_hr import (
    ActiviteMensuelleHRGenerator,
)
from app.services.document_generation.concrete_generators.situation_des_programmes_hr import (
    SituationDesProgrammesHRGenerator,
)
from app.services.document_generation.models.document_specification import (
    DocumentCategory,
    DocumentSpecification,
)
from app.services.document_generation.enums.space_time import Periodicity


@final
class DocumentRegistry(object):
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
                r"^Journal_paiements__Agence_[A-Z+]+_\d{2}\.\d{2}\.\d{4}_[0-9]+.xlsx$": "paiements",
            },
            queries={
                "programmes": """
                SELECT programme
                FROM programmes
                ORDER BY display_order
                """,
                "lancements_mois": """
                SELECT 
                    p.programme,
                    COALESCE(data.count, 0) as count
                FROM programmes p
                LEFT JOIN (
                    SELECT
                        Programme,
                        COUNT(*) as count
                    FROM paiements
                    WHERE Tranche IN (
                            '20%  1 ERE TRANCHE',
                            '40%  Première Tranche',
                            '60%  Première Tranche',
                            '60%  1+2 EME TRANCHE',
                            '100%  Tranche totale',
                            '100%  1+2+3 EME TRANCHE'
                        )
                        AND "Date OV" >= '{month_start}' 
                        AND "Date OV" <= '{month_end}'
                    GROUP BY Programme
                ) data ON p.programme = data.Programme
                ORDER BY p.display_order
                """,
                "lancements_cumul_annee": """
                SELECT 
                    p.programme,
                    COALESCE(data.count, 0) as count
                FROM programmes p
                LEFT JOIN (
                    SELECT
                        Programme,
                        COUNT(*) as count
                    FROM paiements
                    WHERE Tranche IN (
                            '20%  1 ERE TRANCHE',
                            '40%  Première Tranche',
                            '60%  Première Tranche',
                            '60%  1+2 EME TRANCHE',
                            '100%  Tranche totale',
                            '100%  1+2+3 EME TRANCHE'
                        )
                        AND "Date OV" >= '{year}-01-01' 
                        AND "Date OV" <= '{month_end}'
                    GROUP BY Programme
                ) data ON p.programme = data.Programme
                ORDER BY p.display_order
                """,
                "livraisons_mois": """
                SELECT
                    p.programme,
                    COALESCE(data.count, 0) as count
                FROM programmes p
                LEFT JOIN (
                    SELECT
                        Programme,
                        COUNT(*) as count
                    FROM paiements
                    WHERE Tranche IN (
                            '40%  3 EME TRANCHE',
                            '40%  Deuxième Tranche',
                            '60%  Deuxième Tranche',
                            '80%  2+3 EME TRANCHE',
                            '100%  1+2+3 EME TRANCHE',
                            'Tranche complémentaire 2'
                        )
                        AND "Date OV" >= '{month_start}' 
                        AND "Date OV" <= '{month_end}'
                    GROUP BY Programme
                ) data ON p.programme = data.Programme
                ORDER BY p.display_order
                """,
                "livraisons_cumul_annee": """
                SELECT 
                    p.programme,
                    COALESCE(data.count, 0) as count
                FROM programmes p
                LEFT JOIN (
                    SELECT
                        Programme,
                        COUNT(*) as count
                    FROM paiements
                    WHERE Tranche IN (
                            '40%  3 EME TRANCHE',
                            '40%  Deuxième Tranche',
                            '60%  Deuxième Tranche',
                            '80%  2+3 EME TRANCHE',
                            '100%  1+2+3 EME TRANCHE',
                            'Tranche complémentaire 2'
                        )
                        AND "Date OV" >= '{year}-01-01' 
                        AND "Date OV" <= '{month_end}'
                    GROUP BY Programme
                ) data ON p.programme = data.Programme
                ORDER BY p.display_order
                """,
            },
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
