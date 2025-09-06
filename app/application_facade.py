from __future__ import annotations

# Standard library imports
from typing import Any

# Local application imports
from app.services.document_generation.generator_template import DocumentGenerator
from app.data.data_repository import DuckDBRepository
from app.services.document_generation.documents_registry import DocumentRegistry
from app.services.document_generation.documents_registry import DocumentSpecification
from app.services.file_storage.file_storage_service import FileStorageService
from app.services.document_generation.context_management.context_factory import (
    DocumentContextFactory,
)
from app.services.document_generation.context_management.document_context import (
    DocumentContext,
)
from app.utils.space_time import Wilaya
from app.config import AppConfig
from app.services.document_generation.generator_factory import DocumentGeneratorFactory


class ApplicationFacade(object):  # Facade pattern
    __slots__ = (
        "_config",
        "_data_repository",
        "_storage_service",
    )

    def __init__(self, config: AppConfig) -> None:
        # Dependency injection pattern
        self._config: AppConfig = config
        self._data_repository: DuckDBRepository = DuckDBRepository(
            self._config.database_config
        )
        self._storage_service: FileStorageService = FileStorageService(
            self._config.storage_config
        )

    def __enter__(self) -> ApplicationFacade:
        self._data_repository.__enter__()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self._data_repository.__exit__(exc_type, exc_val, exc_tb)

    def generate_document(
        self, document_name: str, output_path: str | None = None
    ) -> None:
        try:
            if not DocumentRegistry.has(document_name):
                available_docs = list(DocumentRegistry.all().keys())
                raise ValueError(
                    f"Unknown document: {document_name}. Available: {available_docs}"
                )

            # Get document specification
            document_specification: DocumentSpecification = DocumentRegistry.get(
                document_name
            )
            print(f"Generating document: {document_specification.display_name}")

            # Create document spatiotemporal context
            document_context: DocumentContext = DocumentContextFactory.create_context(
                wilaya=Wilaya.TIZI_OUZOU, periodicity=document_specification.periodicity
            )

            # Create generator and generate document
            generator: DocumentGenerator = DocumentGeneratorFactory.create_generator(
                document_name,
                self._storage_service,
                self._data_repository,
                document_context,
            )

            # Determine output path
            if output_path is None:
                output_path = f"{document_specification.output_filename}.xlsx"

            generator.generate()
            print(f"Document generated successfully: {output_path}")

        except Exception:
            raise

    def get_available_documents(self) -> dict[str, Any]:
        return DocumentRegistry.all()
