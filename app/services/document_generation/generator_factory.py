from __future__ import annotations

# Local application imports
from app.data.data_repository import DataRepository
from app.services.document_generation.concrete_generators.activite_mensuelle_hr import (
    ActiviteMensuelleHRGenerator,
)
from app.services.document_generation.concrete_generators.situation_des_programmes_hr import (
    SituationDesProgrammesHRGenerator,
)
from app.services.document_generation.context_management.document_context import (
    DocumentContext,
)
from app.services.document_generation.documents_registry import (
    DocumentRegistry,
    DocumentSpecification,
)
from app.services.document_generation.generator_template import DocumentGenerator
from app.services.file_storage.file_storage_service import FileStorageService


class DocumentGeneratorFactory:
    _generators: dict[str, type[DocumentGenerator]] = {
        "activite_mensuelle_par_programme": ActiviteMensuelleHRGenerator,
        "situation_des_programmes": SituationDesProgrammesHRGenerator,
    }

    @classmethod
    def create_generator(
        cls,
        document_name: str,
        storage_service: FileStorageService,
        data_repository: DataRepository,
        document_context: DocumentContext,
    ) -> DocumentGenerator:
        if document_name not in cls._generators:
            raise ValueError(f"Unknown document: {document_name}")

        document_specification: DocumentSpecification = DocumentRegistry.get(
            document_name
        )
        generator_class: type[DocumentGenerator] = cls._generators[document_name]
        return generator_class(
            storage_service, data_repository, document_specification, document_context
        )
