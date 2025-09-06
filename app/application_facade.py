from __future__ import annotations
from typing import Any

# Local application imports
from app.services.document_generation.generator_template import DocumentGenerator
from app.data.data_repository import DuckDBRepository
from app.services.document_generation.documents_registry import DocumentRegistry
from app.services.document_generation.documents_registry import DocumentSpecification
from app.config import AppConfig, config
from app.services.file_storage.file_storage_service import FileStorageService


class ApplicationFacade(object):  # Facade pattern
    __slots__ = (
        "_config",
        "_data_repository",
        "_storage_service",
    )

    def __init__(self) -> None:
        # Dependency injection pattern
        self._config: AppConfig = config
        self._data_repository: DuckDBRepository = DuckDBRepository(
            self._config.database_config
        )
        self._storage_service: FileStorageService = FileStorageService(
            self._config.storage_config
        )

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
            doc_spec: DocumentSpecification = DocumentRegistry.get(document_name)
            print(f"Generating document: {doc_spec.display_name}")

            # Create generator and generate document
            generator: DocumentGenerator = doc_spec.generator(
                self._storage_service, self._data_repository
            )

            # Determine output path
            if output_path is None:
                output_path = f"{doc_spec.output_filename}.xlsx"

            generator.generate()
            print(f"✓ Document generated successfully: {output_path}")

        except Exception:
            raise
        finally:
            self._cleanup()

    def get_available_documents(self) -> dict[str, Any]:
        return DocumentRegistry.all()

    def _cleanup(self) -> None:
        self._data_repository.close()
