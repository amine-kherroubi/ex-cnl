from __future__ import annotations

# Standard library imports
from pathlib import Path

# Third-party imports
import duckdb
import pandas as pd

connection: duckdb.DuckDBPyConnection = duckdb.connect()  # type: ignore

queries: dict[str, str] = {
    "query1": """
        SELECT DISTINCT Programme,
                MIN(STRPTIME("Date OV", '%d/%m/%Y')) AS first_date,
                MAX(STRPTIME("Date OV", '%d/%m/%Y')) AS last_date,
                COUNT(*) AS OVs
        FROM paiements
        GROUP BY Programme
        ORDER BY first_date
    """,
    "query2": """
        SELECT DISTINCT "Sous program"
        FROM decisions
    """,
    "query3": """
        SELECT DISTINCT Programme,
                "Sous program"
        FROM paiements
    """,
    "query4": """
        SELECT DISTINCT Daira
        FROM paiements
        ORDER BY Daira
    """,
    "query5": """
        SELECT DISTINCT "Commune de projet"
        FROM paiements
        ORDER BY "Commune de projet"
    """,
    "query6": """
        SELECT DISTINCT
            p."Sous program",
            p."Notification"
        FROM paiements p
        ORDER BY p."Sous program", p."Notification"
    """,
}


def run_query(name: str) -> None:
    if name not in queries:
        raise ValueError(f"Query {name!r} not found.")

    sql: str = queries[name]

    if "paiements" in sql:
        df: pd.DataFrame = pd.read_excel(  # type: ignore
            "/mnt/c/Users/user/Documents/Stage/applic HR/Journal_paiements__Agence_TIZI+OUZOU_04.09.2025_8728206523967732398.xlsx",
            skiprows=5,
        )
        connection.register("paiements", df)
    if "decisions" in sql:
        df: pd.DataFrame = pd.read_excel(  # type: ignore
            "/mnt/c/Users/user/Documents/Stage/applic HR/Journal_décisions__Agence_TIZI+OUZOU_04.09.2025_5676342332124433611.xlsx",
            skiprows=6,
        )
        connection.register("decisions", df)

    result: pd.DataFrame = connection.execute(sql).fetch_df()
    out_file: Path = Path(f"{name}_result.txt")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(result.to_string(index=False))  # type: ignore
    print(f"Wrote {name} results to {out_file.resolve()}")


if __name__ == "__main__":
    run_query("query6")
