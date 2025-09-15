from __future__ import annotations

# Standard library imports
from typing import Any, Protocol
from logging import Logger

# Third-party imports
import duckdb
import pandas as pd

# Local application imports
from app.utils.exceptions import DatabaseError, QueryExecutionError
from app.config import DatabaseConfig
from app.utils.logging_setup import get_logger


class DataRepository(Protocol):
    def create_table_from_dataframe(
        self,
        table_name: str,
        dataframe: pd.DataFrame,
    ) -> None: ...
    def execute(self, query: str) -> pd.DataFrame: ...
    def count_records(self, table_name: str) -> int: ...
    def describe(self, table_name: str) -> pd.DataFrame: ...
    def get_data(
        self,
        table_name: str,
        offset: int = 0,
        limit: int = 5,
    ) -> pd.DataFrame: ...
    def summarize(self, table_name: str) -> dict[str, Any]: ...
    def close(self) -> None: ...


class DuckDBRepository:
    __slots__ = (
        "_config",
        "_connection",
        "_data_loaded",
        "_logger",
    )

    def __init__(self, db_config: DatabaseConfig) -> None:
        self._logger: Logger = get_logger(__name__)
        self._logger.debug("Initializing DuckDB repository")

        self._config: DatabaseConfig = db_config

        config_dict: dict[str, Any] = {
            "max_memory": db_config.max_memory if db_config.max_memory else "1GB",
        }
        self._logger.debug(f"DuckDB configuration: {config_dict}")

        self._connection: duckdb.DuckDBPyConnection | None
        if db_config.path:
            self._logger.info(f"Connecting to DuckDB file: {db_config.path}")
            self._connection = duckdb.connect(  # type: ignore
                database=db_config.path, config=config_dict
            )
        else:
            self._logger.info("Creating in-memory DuckDB connection")
            self._connection = duckdb.connect(database=":memory:", config=config_dict)  # type: ignore

        if db_config.enable_logging:
            if not self._connection:
                error_msg: str = "Failed to initialize DuckDB connection"
                self._logger.error(error_msg)
                raise DatabaseError(error_msg)
            self._logger.debug("Enabling DuckDB query logging")
            self._connection.execute("PRAGMA enable_logging;")

        self._data_loaded: bool = False
        self._logger.info("DuckDB repository initialized successfully")

    def create_table_from_dataframe(
        self, table_name: str, dataframe: pd.DataFrame
    ) -> None:
        self._logger.debug(
            f"Creating table '{table_name}' from DataFrame with shape {dataframe.shape}"
        )

        if not self._connection:
            error_msg: str = "Connection is closed"
            self._logger.error(error_msg)
            raise DatabaseError(error_msg)

        try:
            self._connection.register(table_name, dataframe)
            self._data_loaded = True
            rows, cols = dataframe.shape
            self._logger.info(
                f"Table '{table_name}' created successfully: {rows} rows and {cols} columns"
            )

        except Exception as error:
            error_msg: str = f"Failed to create table '{table_name}': {error}"
            self._logger.exception(error_msg)
            raise DatabaseError(error_msg) from error

    def execute(self, query: str) -> pd.DataFrame:
        self._logger.debug(
            f"Executing query: {query[:100]}{'...' if len(query) > 100 else ''}"
        )

        if not self._connection:
            error_msg: str = "Connection is closed"
            self._logger.error(error_msg)
            raise DatabaseError(error_msg)

        if not self._data_loaded:
            error_msg: str = "No data loaded in repository"
            self._logger.error(error_msg)
            raise DatabaseError(error_msg)

        try:
            result: pd.DataFrame = self._connection.execute(query).fetchdf()
            self._logger.debug(
                f"Query returned: {len(result)} rows and {len(result.columns)} columns"
            )
            return result
        except Exception as error:
            self._logger.exception(f"Query execution failed: {error}")
            raise QueryExecutionError(query, error) from error

    def count_records(self, table_name: str) -> int:
        self._logger.debug(f"Counting records in table '{table_name}'")
        result: pd.DataFrame = self.execute(
            f"SELECT COUNT(*) as total_rows FROM {table_name}"
        )
        count: int = int(result["total_rows"].iloc[0])
        self._logger.debug(f"Table '{table_name}' contains {count} records")
        return count

    def describe(self, table_name: str) -> pd.DataFrame:
        self._logger.debug(f"Describing structure of table '{table_name}'")
        result: pd.DataFrame = self.execute(f"DESCRIBE {table_name}")
        self._logger.debug(f"Table '{table_name}' has {len(result)} columns")
        return result

    def get_data(
        self, table_name: str, offset: int = 0, limit: int = 5
    ) -> pd.DataFrame:
        self._logger.debug(
            f"Retrieving sample from table '{table_name}' (offset={offset}, limit={limit})"
        )
        result: pd.DataFrame = self.execute(
            f"SELECT * FROM {table_name} OFFSET {offset} LIMIT {limit}"
        )
        self._logger.debug(
            f"Retrieved {len(result)} sample rows from table '{table_name}'"
        )
        return result

    def summarize(self, table_name: str) -> dict[str, Any]:
        self._logger.debug(f"Generating summary for table '{table_name}'")
        try:
            summary: dict[str, Any] = {
                "total_records": self.count_records(table_name),
                "table_description": self.describe(table_name),
                "sample_data": self.get_data(table_name),
            }
            self._logger.info(
                f"Summary generated for table '{table_name}' with {summary['total_records']} records"
            )
            return summary
        except Exception as error:
            self._logger.exception(
                f"Failed to generate summary for table '{table_name}': {error}"
            )
            return {}

    def close(self) -> None:
        if not self._connection:
            self._logger.debug("Connection already closed")
            return

        self._logger.info("Closing DuckDB connection")
        self._connection.close()
        self._connection = None
        self._logger.debug("DuckDB connection closed successfully")
