from __future__ import annotations

# Standard library imports
import shutil
from pathlib import Path
from typing import Any

# Local application imports
from app.application_facade import ApplicationFacade
from app.config import AppConfig, FileIOConfig, DatabaseConfig


class DocumentController:
    __slots__ = ("_temp_dir", "_uploads_dir", "_results_dir", "_config", "_facade")

    def __init__(self) -> None:
        # Initialize app config with temporary directories
        self._temp_dir: Path = Path.cwd() / "temp"
        self._temp_dir.mkdir(exist_ok=True)

        self._uploads_dir: Path = self._temp_dir / "uploads"
        self._uploads_dir.mkdir(exist_ok=True)

        self._results_dir: Path = self._temp_dir / "results"
        self._results_dir.mkdir(exist_ok=True)

        # Create storage config
        storage_config: FileIOConfig = FileIOConfig(
            uploads_dir=self._uploads_dir,
            results_dir=self._results_dir,
        )

        # Create database config (in-memory)
        database_config: DatabaseConfig = DatabaseConfig(
            path=None,  # In-memory database
        )

        # Create app config
        self._config: AppConfig = AppConfig(
            storage_config=storage_config,
            database_config=database_config,
        )

        # Initialize facade
        self._facade: ApplicationFacade = ApplicationFacade(self._config)

    def get_available_reports(self) -> dict[str, Any]:
        return self._facade.get_available_documents()

    def generate_document(
        self, report_name: str, input_files: list[Path], output_path: Path
    ) -> str:
        try:
            # Copy input files to temp uploads directory
            self._prepare_input_files(input_files=input_files)

            # Generate the document (it will be saved to temp results)
            self._facade.generate_document(document_name=report_name)

            # Find and move the generated file to the desired output location
            generated_file: Path = self._find_generated_file()
            final_output_path: Path = output_path / generated_file.name

            # Move file to final destination
            shutil.move(src=str(generated_file), dst=str(final_output_path))

            # Cleanup temp files
            self._cleanup_temp_files()

            return str(final_output_path)

        except Exception as e:
            # Cleanup on error
            self._cleanup_temp_files()
            raise e

    def _prepare_input_files(self, input_files: list[Path]) -> None:
        # Clear existing files
        for existing_file in self._uploads_dir.iterdir():
            if existing_file.is_file():
                existing_file.unlink()

        # Copy new files
        for file_path in input_files:
            if file_path.exists():
                destination: Path = self._uploads_dir / file_path.name
                shutil.copy2(src=str(file_path), dst=str(destination))

    def _find_generated_file(self) -> Path:
        result_files: list[Path] = list(self._results_dir.glob(pattern="*.xlsx"))

        if not result_files:
            raise FileNotFoundError("No generated file found")

        if len(result_files) > 1:
            raise ValueError(f"Multiple generated files found: {result_files}")

        return result_files[0]

    def _cleanup_temp_files(self) -> None:
        for temp_file in self._uploads_dir.iterdir():
            if temp_file.is_file():
                temp_file.unlink()

        for temp_file in self._results_dir.iterdir():
            if temp_file.is_file():
                temp_file.unlink()
