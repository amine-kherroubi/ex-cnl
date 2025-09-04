from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final, final


class DocumentCategory(StrEnum):
    HR = "HR"
    AAP = "AAP"


@dataclass
class DocumentDefinition(object):
    name: str
    display_name: str
    category: DocumentCategory
    description: str
    required_files: list[str]
    queries: dict[str, str]
    output_filename: str


@final
class DocumentRegistry(object):  # Registry pattern
    def __new__(cls):
        raise RuntimeError(
            "DocumentRegistry cannot be instantiated. Use class methods."
        )

    @classmethod
    def get(cls, document_name: str) -> DocumentDefinition:
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
    def all(cls) -> MappingProxyType[str, DocumentDefinition]:
        return MappingProxyType(
            cls._DOCUMENTS_DEFINITIONS
        )  # MappingProxyType implements the proxy pattern

    _DOCUMENTS_DEFINITIONS: Final[dict[str, DocumentDefinition]] = {
        "activite_mensuelle_par_programme": DocumentDefinition(
            name="activite_mensuelle_par_programme",
            display_name="Activité mensuelle par programme",
            category=DocumentCategory.HR,
            description=(
                "Document de suivi mensuel des activités par programme, "
                "renseigné par la BNH (ex-CNL)"
            ),
            required_files=[
                r"^Journal_décisions__Agence_[A-Z+]+_\d{2}\.\d{2}\.\d{4}_[0-9]+$",
                r"^Journal_payements__Agence_[A-Z+]+_\d{2}\.\d{2}\.\d{4}_[0-9]+$",
            ],
            queries={
                "total_amount": "SELECT SUM(amount) FROM line_items",
                "vendor_info": "SELECT vendor_name, vendor_id FROM vendors",
            },
            output_filename="Activité_mensuelle_par_programme",
        ),
        "situation_des_programmes": DocumentDefinition(
            name="situation_des_programmes",
            display_name="Situation des programmes",
            category=DocumentCategory.HR,
            description=(
                "Document de suivi de la situation des programmes, "
                "renseigné par la BNH (ex-CNL)"
            ),
            required_files=[
                r"^Journal_décisions__Agence_[A-Z+]+_\d{2}\.\d{2}\.\d{4}_[0-9]+$",
                r"^Journal_payements__Agence_[A-Z+]+_\d{2}\.\d{2}\.\d{4}_[0-9]+$",
            ],
            queries={
                "total_amount": "SELECT SUM(amount) FROM line_items",
                "vendor_info": "SELECT vendor_name, vendor_id FROM vendors",
            },
            output_filename="Situation_des_programmes",
        ),
    }
