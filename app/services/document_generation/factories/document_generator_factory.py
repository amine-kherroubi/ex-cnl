from __future__ import annotations

# Standard library imports
from logging import Logger

# Local application imports
from app.data.data_repository import DataRepository
from app.services.document_generation.concrete_generators.activite_mensuelle_hr import (
    ActiviteMensuelleHRGenerator,
)
from app.services.document_generation.concrete_generators.situation_des_programmes_hr import (
    SituationDesProgrammesHRGenerator,
)
from app.services.document_generation.models.document_context import (
    DocumentContext,
)
from app.services.document_generation.document_registry import (
    DocumentRegistry,
    DocumentSpecification,
)
from app.services.document_generation.document_generator_template import (
    DocumentGenerator,
)
from app.services.file_storage.file_storage_service import FileStorageService
from app.utils.logging_setup import get_logger


class DocumentGeneratorFactory:
    _logger: Logger = get_logger("app.services.generator_factory")

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
        cls._logger.info(f"Creating generator for document: {document_name}")
        cls._logger.debug(f"Available generators: {list(cls._generators.keys())}")

        if document_name not in cls._generators:
            error_msg = f"Unknown document: {document_name}"
            cls._logger.error(f"{error_msg}. Available: {list(cls._generators.keys())}")
            raise ValueError(error_msg)

        try:
            # Get document specification
            document_specification: DocumentSpecification = DocumentRegistry.get(
                document_name
            )
            cls._logger.debug(
                f"Retrieved document specification: {document_specification.display_name}"
            )

            # Get generator class
            generator_class: type[DocumentGenerator] = cls._generators[document_name]
            cls._logger.debug(f"Using generator class: {generator_class.__name__}")

            # Create generator instance
            generator = generator_class(
                storage_service,
                data_repository,
                document_specification,
                document_context,
            )

            cls._logger.info(
                f"Successfully created {generator_class.__name__} for document '{document_name}'"
            )
            cls._logger.debug(
                f"Generator context: wilaya={document_context.wilaya.value}, date={document_context.report_date}"
            )

            return generator

        except Exception as error:
            cls._logger.error(
                f"Failed to create generator for document '{document_name}': {error}"
            )
            raise
