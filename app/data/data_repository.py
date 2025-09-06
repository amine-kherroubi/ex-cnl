from __future__ import annotations

# Standard library imports
from typing import Any, Protocol

# Third-party imports
import duckdb
import pandas

# Local application imports
from app.utils.exceptions import DatabaseError, QueryExecutionError
from app.config import DatabaseConfig


class DataRepository(Protocol):  # Repository pattern with protocol
    def create_view_from_dataframe(
        self,
        view_name: str,
        dataframe: pandas.DataFrame,
    ) -> None: ...
    def execute(self, query: str) -> pandas.DataFrame: ...
    def count_records(self, view_name: str) -> int: ...
    def describe(self, view_name: str) -> pandas.DataFrame: ...
    def get_data(
        self,
        view_name: str,
        offset: int = 0,
        limit: int = 5,
    ) -> pandas.DataFrame: ...
    def summarize(self, view_name: str) -> dict[str, Any]: ...
    def close(self) -> None: ...


class DuckDBRepository:  # Repository pattern implementation
    __slots__ = (
        "_config",
        "_connection",
        "_data_loaded",
    )

    def __init__(self, db_config: DatabaseConfig) -> None:
        self._config: DatabaseConfig = db_config

        config_dict: dict[str, Any] = {
            "max_memory": db_config.max_memory if db_config.max_memory else "1GB",
        }

        self._connection: duckdb.DuckDBPyConnection | None
        if db_config.path:
            self._connection = duckdb.connect(database=db_config.path, config=config_dict)  # type: ignore
        else:
            self._connection = duckdb.connect(database=":memory:", config=config_dict)  # type: ignore

        if db_config.enable_logging:
            if not self._connection:
                raise DatabaseError("Failed to initialize DuckDB connection")
            self._connection.execute("PRAGMA enable_logging;")

        self._data_loaded: bool = False

    def create_view_from_dataframe(
        self, view_name: str, dataframe: pandas.DataFrame
    ) -> None:
        if not self._connection:
            raise DatabaseError("Connection is closed")
        self._connection.register(view_name, dataframe)
        self._data_loaded = True

    def execute(self, query: str) -> pandas.DataFrame:
        if not self._connection:
            raise DatabaseError("Connection is closed")
        if not self._data_loaded:
            raise DatabaseError("No data loaded")

        try:
            return self._connection.execute(query).fetchdf()
        except Exception as error:
            raise QueryExecutionError(query, error) from error

    def count_records(self, view_name: str) -> int:
        result = self.execute(f"SELECT COUNT(*) as total_rows FROM {view_name}")
        return int(result["total_rows"].iloc[0])

    def describe(self, view_name: str) -> pandas.DataFrame:
        return self.execute(f"DESCRIBE {view_name}")

    def get_data(
        self, view_name: str, offset: int = 0, limit: int = 5
    ) -> pandas.DataFrame:
        return self.execute(f"SELECT * FROM {view_name} OFFSET {offset} LIMIT {limit}")

    def summarize(self, view_name: str) -> dict[str, Any]:
        try:
            return {
                "total_records": self.count_records(view_name),
                "table_description": self.describe(view_name),
                "sample_data": self.get_data(view_name),
            }
        except Exception:
            return {}

    def close(self) -> None:
        if not self._connection:
            return
        self._connection.close()
        self._connection = None
