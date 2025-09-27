from __future__ import annotations

# Standard library imports
from pathlib import Path

# Third-party imports
import duckdb
import pandas as pd

connection: duckdb.DuckDBPyConnection = duckdb.connect()  # type: ignore

queries: dict[str, str] = {}


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

    if "subprograms" in sql:
        from app.core.domain.registries.subprogram_registry import SubprogramRegistry

        df: pd.DataFrame = SubprogramRegistry.get_subprograms_dataframe()
        connection.register("subprograms", df)

    if "dairas_communes" in sql:
        from app.core.domain.predefined_objects.dairas_et_communes import (
            get_dairas_communes_dataframe,
        )

        df: pd.DataFrame = get_dairas_communes_dataframe()
        connection.register("dairas_communes", df)

    result: pd.DataFrame = connection.execute(sql).fetch_df()
    out_file: Path = Path(f"{name}_result.txt")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(result.to_string(index=False))  # type: ignore
    print(f"Wrote {name} results to {out_file.resolve()}")


if __name__ == "__main__":
    pass
