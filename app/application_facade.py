from __future__ import annotations
from pathlib import Path
from app.services.document_generation.generator_template import DocumentGenerator
from app.data.data_repository import DuckDBRepository
from app.services.document_generation.documents_registry import DocumentRegistry
from app.services.document_generation.generators.activite_mensuelle_hr import (
    ActiviteMensuelleHRGenerator,
)
from app.services.document_generation.generators.situation_des_programmes_hr import (
    SituationDesProgrammesHRGenerator,
)
from app.services.document_generation.documents_registry import DocumentDefinition


class ApplicationFacade(object):  # Facade pattern
    def __init__(self) -> None:
        # Hardcoded configuration
        self._enable_debug = True

        # Dependency injection pattern
        self._repository: DuckDBRepository = DuckDBRepository()

        # Document generators registry
        self._generators: dict[str, type[DocumentGenerator]] = {
            "activite_mensuelle_par_programme": ActiviteMensuelleHRGenerator,
            "situation_des_programmes": SituationDesProgrammesHRGenerator,
        }

    def generate_document(
        self, document_name: str, output_path: str | None = None
    ) -> None:
        """Generate a specific document by name"""
        try:
            if not DocumentRegistry.has(document_name):
                available_docs = list(DocumentRegistry.all().keys())
                raise ValueError(
                    f"Unknown document: {document_name}. Available: {available_docs}"
                )

            if document_name not in self._generators:
                raise ValueError(
                    f"No generator available for document: {document_name}"
                )

            # Get document definition
            doc_def: DocumentDefinition = DocumentRegistry.get(document_name)
            print(f"Generating document: {doc_def.display_name}")
            print(f"Category: {doc_def.category}")
            print(f"Description: {doc_def.description}")

            # Check for required files in current directory
            self._check_required_files(doc_def.required_files)

            # Load data from required files (this will be handled by the generator's validation)
            # For now, we just create a dummy connection since the actual file loading
            # happens in the generator's _validate_required_files method

            # Create generator and generate document
            generator_class: type[DocumentGenerator] = self._generators[document_name]
            generator: DocumentGenerator = generator_class(self._repository)

            # Determine output path
            if output_path is None:
                output_path = f"{doc_def.output_filename}.xlsx"

            generator.generate(output_path)
            print(f"✓ Document generated successfully: {output_path}")

        except Exception:
            raise
        finally:
            self._cleanup()

    def list_available_documents(self) -> None:
        """List all available documents that can be generated"""
        print("Available documents:")
        print("-" * 60)

        for doc_name, doc_def in DocumentRegistry.all().items():
            status = "✓ Available" if doc_name in self._generators else "✗ No generator"
            print(f"• {doc_def.display_name}")
            print(f"  Name: {doc_name}")
            print(f"  Category: {doc_def.category}")
            print(f"  Status: {status}")
            print(f"  Description: {doc_def.description}")
            print(f"  Required files (patterns):")
            for pattern in doc_def.required_files:
                print(f"    - {pattern}")
            print()

    def _check_required_files(self, required_patterns: list[str]) -> None:
        """Check if required files exist in current working directory"""
        import re

        current_dir: Path = Path.cwd()
        available_files: list[str] = [
            p.name for p in current_dir.iterdir() if p.is_file()
        ]

        print(f"Checking for required files in: {current_dir}")
        print(f"Available files: {available_files}")

        missing_patterns: list[str] = []
        for pattern in required_patterns:
            regex: re.Pattern[str] = re.compile(pattern)
            matching_files: list[str] = [
                file_name for file_name in available_files if regex.match(file_name)
            ]

            if not matching_files:
                missing_patterns.append(pattern)
            else:
                print(f"✓ Found files matching '{pattern}': {matching_files}")

        if missing_patterns:
            print("✗ Missing required files matching patterns:")
            for pattern in missing_patterns:
                print(f"  - {pattern}")
            raise FileNotFoundError(
                f"Missing required files. Please ensure files matching these patterns are in the current directory: {missing_patterns}"
            )

    def _cleanup(self) -> None:
        """Clean up resources"""
        if hasattr(self, "_repository") and self._repository:
            self._repository.close()
