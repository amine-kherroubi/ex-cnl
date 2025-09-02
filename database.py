from __future__ import annotations
from pathlib import Path
import duckdb
import pandas


class Database:
    def __init__(self, connection: duckdb.DuckDBPyConnection | None = None):
        self.connection: duckdb.DuckDBPyConnection = connection or duckdb.connect()  # type: ignore

    def setup_from_excel(self, file_path: str) -> None:
        excel_path: Path = Path(file_path)
        if not excel_path.exists():
            raise FileNotFoundError(f"File not found: {excel_path}")

        try:
            print(f"Loading Excel file: {excel_path}")
            dataframe: pandas.DataFrame = pandas.read_excel(  # type: ignore
                excel_path, dtype_backend="numpy_nullable"
            )
            print(
                f"Successfully loaded {len(dataframe)} rows and {len(dataframe.columns)} columns"
            )
            self.connection.register("ovs", dataframe)
            print("Data registered with DuckDB successfully")
            self.connection.execute(
                "CREATE OR REPLACE TABLE commune AS SELECT DISTINCT Commune FROM ovs WHERE Commune IS NOT NULL"
            )
            print("Commune lookup table created")

        except Exception as e:
            print(f"Error loading Excel file: {e}")
            raise

    def execute_query(self, query: str) -> pandas.DataFrame | None:
        try:
            result: pandas.DataFrame = self.connection.execute(query).fetchdf()
            return result
        except Exception as error:
            print(f"Query execution failed: {error}")
            return None

    def debug_data_structure(self) -> None:
        try:
            table_info: pandas.DataFrame = self.connection.execute(
                "DESCRIBE ovs"
            ).fetchdf()
            print("Table structure:")
            print(f"\n{table_info}")

            sample_data: pandas.DataFrame = self.connection.execute(
                "SELECT * FROM ovs LIMIT 5"
            ).fetchdf()
            print("Sample data (first 5 rows):")
            print(f"\n{sample_data}")

            count: pandas.DataFrame = self.connection.execute(
                "SELECT COUNT(*) as total_rows FROM ovs"
            ).fetchdf()
            print(f"Total rows in dataset: {count['total_rows'].iloc[0]}")

        except Exception as e:
            print(f"Error during debugging: {e}")

    def close(self) -> None:
        if self.connection:
            self.connection.close()
            print("Database connection closed")
