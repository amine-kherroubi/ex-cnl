from __future__ import annotations

from typing import Final


class ApplicationError(Exception):
    __slots__ = ()

    pass


class DatabaseError(ApplicationError):
    __slots__ = ()

    pass


class FileProcessingError(ApplicationError):
    __slots__ = ()

    pass


class QueryExecutionError(DatabaseError):
    __slots__ = (
        "query",
        "original_error",
    )

    def __init__(self, query: str, original_error: Exception) -> None:
        self.query: Final[str] = query
        self.original_error: Final[Exception] = original_error
        super().__init__(f"Query execution failed: {original_error}")


class DataLoadError(DatabaseError):
    __slots__ = (
        "file_path",
        "original_error",
    )

    def __init__(self, file_path: str, original_error: Exception) -> None:
        self.file_path: Final[str] = file_path
        self.original_error: Final[Exception] = original_error
        super().__init__(f"Failed to load data from {file_path}: {original_error}")
