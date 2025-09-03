from __future__ import annotations
from typing import Final


class ApplicationError(Exception):
    pass


class DatabaseError(ApplicationError):
    pass


class FileProcessingError(ApplicationError):
    pass


class QueryExecutionError(DatabaseError):
    def __init__(self, query: str, original_error: Exception) -> None:
        self.query: Final[str] = query
        self.original_error: Final[Exception] = original_error
        super().__init__(f"Query execution failed: {original_error}")


class DataLoadError(DatabaseError):
    def __init__(self, file_path: str, original_error: Exception) -> None:
        self.file_path: Final[str] = file_path
        self.original_error: Final[Exception] = original_error
        super().__init__(f"Failed to load data from {file_path}: {original_error}")
