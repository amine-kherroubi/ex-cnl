import duckdb
import pandas as pd
from pathlib import Path

connection: duckdb.DuckDBPyConnection = duckdb.connect()  # type: ignore
df: pd.DataFrame = pd.read_excel(Path(""), skiprows=5)  # type: ignore
connection.register("paiements", df)

# query1_result: pd.DataFrame = connection.execute(
#     """
#     SELECT DISTINCT Programme,
#             MIN(STRPTIME("Date OV", '%d/%m/%Y')) AS first_date,
#             MAX(STRPTIME("Date OV", '%d/%m/%Y')) AS last_date,
#             COUNT(*) AS OVs
#     FROM paiements
#     GROUP BY Programme
#     ORDER BY first_date
#     """
# ).fetch_df()
# print(query1_result)

# query2_result: pd.DataFrame = connection.execute(
#     """
#     SELECT DISTINCT "Sous programme",
#             MIN(STRPTIME("Date OV", '%d/%m/%Y')) AS first_date,
#             MAX(STRPTIME("Date OV", '%d/%m/%Y')) AS last_date,
#             COUNT(*) AS OVs
#     FROM paiements
#     GROUP BY "Sous programme"
#     ORDER BY first_date
#     """
# ).fetch_df()
# print(query2_result)

query3_result: pd.DataFrame = connection.execute(
    """
    SELECT DISTINCT Programme,
            "Sous programme"
    FROM paiements
    """
).fetch_df()
print(query3_result)
