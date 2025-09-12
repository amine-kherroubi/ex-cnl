from __future__ import annotations

# Standard library imports
from datetime import date
from logging import Logger
from typing import Any

# Local application imports
from app.services.document_generation.document_generator_template import (
    DocumentGenerator,
)
from app.data.data_repository import DuckDBRepository
from app.services.document_generation.document_registry import DocumentRegistry
from app.services.document_generation.document_registry import DocumentSpecification
from app.services.io.io import IOService
from app.services.document_generation.factories.document_context_factory import (
    DocumentContextFactory,
)
from app.services.document_generation.models.document_context import (
    DocumentContext,
)
from app.services.document_generation.enums.space_time import Wilaya
from app.config import AppConfig
from app.services.document_generation.factories.document_generator_factory import (
    DocumentGeneratorFactory,
)
from app.utils.logging_setup import get_logger


class ApplicationFacade(object):  # Facade pattern
    __slots__ = (
        "_config",
        "_data_repository",
        "_storage_service",
        "_logger",
    )

    def __init__(self, config: AppConfig) -> None:
        # Get logger for this class
        self._logger: Logger = get_logger("app.facade")
        self._logger.debug("Initializing ApplicationFacade")

        # Dependency injection pattern
        self._config: AppConfig = config
        self._data_repository: DuckDBRepository = DuckDBRepository(
            self._config.database_config
        )
        self._storage_service: IOService = IOService(self._config.storage_config)

        self._logger.info("ApplicationFacade initialized successfully")

    def generate_document(
        self, document_name: str, output_path: str | None = None
    ) -> None:
        self._logger.info(f"Starting document generation: {document_name}")

        try:
            if not DocumentRegistry.has(document_name):
                available_docs: list[str] = list(DocumentRegistry.all().keys())
                error_msg: str = (
                    f"Unknown document: {document_name}. Available: {available_docs}"
                )
                self._logger.error(error_msg)
                raise ValueError(error_msg)

            # Get document specification
            document_specification: DocumentSpecification = DocumentRegistry.get(
                document_name
            )
            self._logger.info(
                f"Generating document: {document_specification.display_name}"
            )
            self._logger.debug(f"Document category: {document_specification.category}")
            self._logger.debug(
                f"Required files: {list(document_specification.required_files.keys())}"
            )

            # Create document spatiotemporal context
            document_context: DocumentContext = DocumentContextFactory.create_context(
                wilaya=Wilaya.TIZI_OUZOU,
                periodicity=document_specification.periodicity,
                report_date=date(2025, 9, 6),
            )
            self._logger.debug(
                f"Document context created: {document_context.wilaya.value}, {document_context.report_date}"
            )

            # Create generator and generate document
            generator: DocumentGenerator = DocumentGeneratorFactory.create_generator(
                document_name,
                self._storage_service,
                self._data_repository,
                document_context,
            )
            self._logger.debug(f"Generator created: {generator.__class__.__name__}")

            # Determine output path
            if output_path is None:
                output_path = f"{document_specification.output_filename}.xlsx"
                self._logger.debug(f"Using default output path: {output_path}")
            else:
                self._logger.debug(f"Using specified output path: {output_path}")

            self._logger.info("Starting document generation process")
            generator.generate()

            self._logger.info(f"Document generated successfully: {output_path}")
            print(f"Document generated successfully: {output_path}")

        except FileNotFoundError as e:
            self._logger.error(f"Required files not found: {e}")
            raise
        except ValueError as e:
            self._logger.error(f"Configuration or data error: {e}")
            raise
        except Exception as e:
            self._logger.exception(f"Unexpected error during document generation: {e}")
            raise

    def get_available_documents(self) -> dict[str, Any]:
        self._logger.debug("Retrieving available documents")
        documents: dict[str, DocumentSpecification] = DocumentRegistry.all()
        self._logger.info(f"Found {len(documents)} available document types")
        return documents
