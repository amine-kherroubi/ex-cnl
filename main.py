"""Excel data processor for OV analysis."""

from pathlib import Path
from typing import Any

import duckdb
import pandas as pd
from openpyxl import Workbook


def setup_database(file_path: str) -> duckdb.DuckDBPyConnection:
    """Create database connection and setup tables from Excel file."""
    excel_path: Path = Path(file_path)
    if not excel_path.exists():
        raise FileNotFoundError(f"File not found: {excel_path}")

    connection = duckdb.connect()

    # Check file extension to determine loading method
    if excel_path.suffix.lower() == ".xls":
        # For .xls files, load via pandas first
        dataframe: pd.DataFrame = pd.read_excel(excel_path)
        connection.register("ovs", dataframe)
    elif excel_path.suffix.lower() == ".xlsx":
        # For .xlsx files, DuckDB can read directly
        connection.execute(f"CREATE TABLE ovs AS SELECT * FROM '{excel_path}'")
    else:
        raise ValueError(f"Unsupported file format: {excel_path.suffix}")

    connection.execute(
        "CREATE OR REPLACE TABLE commune AS SELECT DISTINCT Commune FROM ovs"
    )
    return connection


def get_queries() -> dict[str, str]:
    """Return analytical queries."""
    return {
        "first_tranche_count": """
            SELECT c.Commune,
                   COALESCE((SELECT COUNT(*)
                    FROM ovs o
                    WHERE (NOTIFICATION = 'N°: 1132. Du: 16/07/2013. TRANCHE: 2. Montant:    700 000' OR
                           NOTIFICATION = 'N°:1132.Du:16/07/2013.TRANCHE:2.Montant:   700 000') 
                      AND "Sous programme" = 'PQ2013'
                      AND "Annulé?" = 'non'
                      AND Tranche IN ('60%  1+2 EME TRANCHE',
                                      '20%  1 ERE TRANCHE',
                                      '100%  Tranche totale',
                                      '60%  Première Tranche',
                                      '100%  1+2+3 EME TRANCHE',
                                      '40%  Première Tranche')
                      AND o.Commune = c.Commune
                   ), 0) AS tranche_count
            FROM commune c
            ORDER BY c.Commune
        """,
        "second_tranche_count": """
            SELECT c.Commune,
                   COALESCE((SELECT COUNT(*)
                    FROM ovs o
                    WHERE (NOTIFICATION = 'N°: 1132. Du: 16/07/2013. TRANCHE: 2. Montant:    700 000' OR
                           NOTIFICATION = 'N°:1132.Du:16/07/2013.TRANCHE:2.Montant:   700 000') 
                      AND "Sous programme" = 'PQ2013'
                      AND "Annulé?" = 'non'
                      AND Tranche IN ('100%  Tranche totale',
                                      '100%  1+2+3 EME TRANCHE',
                                      '40%  3 EME TRANCHE',
                                      '40%  Deuxième Tranche',
                                      '80%  2+3 EME TRANCHE',
                                      '40%  C2',
                                      '60%  Deuxième Tranche',
                                      'Tranche complémentaire 2')
                      AND o.Commune = c.Commune
                   ), 0) AS tranche_count
            FROM commune c
            ORDER BY c.Commune
        """,
        "total_amount": """
            SELECT c.Commune,
                   COALESCE((SELECT SUM(Montant)
                    FROM ovs o
                    WHERE (NOTIFICATION = 'N°: 1132. Du: 16/07/2013. TRANCHE: 2. Montant:    700 000' OR
                           NOTIFICATION = 'N°:1132.Du:16/07/2013.TRANCHE:2.Montant:   700 000') 
                      AND "Sous programme" = 'PQ2013'
                      AND "Annulé?" = 'non'
                      AND o.Commune = c.Commune
                   ), 0) AS total_amount
            FROM commune c
            ORDER BY c.Commune
        """,
        "initial_program_count": """
            SELECT c.Commune,
                   COALESCE((SELECT COUNT(*)
                    FROM ovs o
                    WHERE (NOTIFICATION = 'N°: 463. Du: 03/03/2011. TRANCHE: 1. Montant:    700 000' OR
                           NOTIFICATION = 'N°:463.Du:03/03/2011.TRANCHE:1.Montant:   700 000') 
                      AND "Sous programme" = 'PROGRAMME INITIAL'
                      AND "Annulé?" = 'non'
                      AND Tranche IN ('40%  2 EME TRANCHE ',
                                      '100%  1+2+3 EME TRANCHE',
                                      '60%  1+2 EME TRANCHE',
                                      '80%  2+3 EME TRANCHE')
                      AND o.Commune = c.Commune
                   ), 0) AS tranche_count
            FROM commune c
            ORDER BY c.Commune
        """,
    }


def execute_query(
    connection: duckdb.DuckDBPyConnection, query: str
) -> pd.DataFrame | None:
    """Execute SQL query and return DataFrame."""
    try:
        result: pd.DataFrame = connection.execute(query).fetchdf()
        return result
    except Exception as error:
        print(f"Query execution failed: {error}")
        return None


def create_excel_sheet(
    workbook: Workbook, sheet_name: str, dataframe: pd.DataFrame
) -> None:
    """Create Excel sheet with data."""
    worksheet: Any = workbook.create_sheet(title=sheet_name)
    worksheet.append(dataframe.columns.tolist())

    for row_data in dataframe.itertuples(index=False, name=None):
        worksheet.append(list(row_data))


def save_results_to_excel(
    queries: dict[str, str], connection: duckdb.DuckDBPyConnection, output_file: str
) -> None:
    """Execute queries and save results to Excel file."""
    workbook: Workbook = Workbook()
    workbook.remove(workbook.active)

    for query_name, query_sql in queries.items():
        result_dataframe: pd.DataFrame | None = execute_query(connection, query_sql)

        if result_dataframe is not None:
            create_excel_sheet(workbook, query_name, result_dataframe)
            print(
                f"Query '{query_name}' executed successfully - {len(result_dataframe)} rows"
            )
        else:
            print(f"Query '{query_name}' failed")

    workbook.save(output_file)


def main() -> None:
    """Main execution function."""
    input_filename: str = (
        "Liste_OVs_Agence_TIZIOUZOU_17.09.2024_7284743114531606447.xlsx"
    )
    output_filename: str = "resultats_requetes.xlsx"

    # Setup database directly from file
    database_connection: duckdb.DuckDBPyConnection = setup_database(input_filename)
    analytical_queries: dict[str, str] = get_queries()

    # Generate reports
    save_results_to_excel(analytical_queries, database_connection, output_filename)

    # Cleanup
    database_connection.close()
    print(f"Results saved to {output_filename}")


if __name__ == "__main__":
    main()
