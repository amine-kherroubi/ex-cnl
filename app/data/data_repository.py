from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import Any, Protocol

# Third-party imports
import duckdb
import pandas

# Local application imports
from app.utils.exceptions import DataLoadError, DatabaseError, QueryExecutionError


class DataRepository(Protocol):  # Repository pattern with protocol
    def load_data(self, file_path: str) -> None: ...
    def execute_query(self, query: str) -> pandas.DataFrame: ...
    def get_record_count(self) -> int: ...
    def get_table_description(self) -> pandas.DataFrame: ...
    def get_sample_data(self, limit: int = 5) -> pandas.DataFrame: ...
    def close(self) -> None: ...


class DuckDBRepository(object):  # Repository pattern implementation
    __slots__ = (
        "_connection",
        "_data_loaded",
    )

    def __init__(self, connection: duckdb.DuckDBPyConnection | None = None) -> None:
        self._connection: duckdb.DuckDBPyConnection = connection or duckdb.connect()  # type: ignore
        self._data_loaded: bool = False

    def load_data(self, file_path: str) -> None:
        excel_path: Path = Path(file_path)

        if not excel_path.exists():
            raise FileNotFoundError(f"File not found: {excel_path}")

        try:
            dataframe: pandas.DataFrame = pandas.read_excel(  # type: ignore
                excel_path, dtype_backend="numpy_nullable"
            )

            self._connection.register("ovs", dataframe)
            self._data_loaded = True

        except Exception as error:
            raise DataLoadError(str(file_path), error) from error

    def execute_query(self, query: str) -> pandas.DataFrame:
        if not self._data_loaded:
            raise DatabaseError("No data loaded")

        try:
            result: pandas.DataFrame = self._connection.execute(query).fetchdf()
            return result
        except Exception as error:
            raise QueryExecutionError(query, error) from error

    def get_record_count(self) -> int:
        result: pandas.DataFrame = self.execute_query(
            "SELECT COUNT(*) as total_rows FROM ovs"
        )
        return int(result["total_rows"].iloc[0])

    def get_table_description(self) -> pandas.DataFrame:
        return self.execute_query("DESCRIBE ovs")

    def get_sample_data(self, limit: int = 5) -> pandas.DataFrame:
        return self.execute_query(f"SELECT * FROM ovs LIMIT {limit}")

    def get_data_summary(self) -> dict[str, Any]:
        try:
            return {
                "total_records": self.get_record_count(),
                "table_description": self.get_table_description(),
                "sample_data": self.get_sample_data(),
            }

        except Exception:
            return {}

    def close(self) -> None:
        if self._connection:
            self._connection.close()
