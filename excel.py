from __future__ import annotations
from typing import Any
from openpyxl import Workbook
import pandas
from database import Database


class ExcelExporter:
    def _create_excel_sheet(
        self, workbook: Workbook, sheet_name: str, dataframe: pandas.DataFrame
    ) -> None:
        worksheet: Any = workbook.create_sheet(title=sheet_name)
        worksheet.append(dataframe.columns.tolist())

        for row_data in dataframe.itertuples(index=False, name=None):
            worksheet.append(list(row_data))

    def save_results_to_excel(
        self, queries: dict[str, str], database: Database, output_file: str
    ) -> None:
        workbook: Workbook = Workbook()
        workbook.remove(workbook.active)  # type: ignore

        for query_name, query_sql in queries.items():
            result_dataframe: pandas.DataFrame | None = database.execute_query(
                query_sql
            )

            if result_dataframe is not None:
                self._create_excel_sheet(workbook, query_name, result_dataframe)
                print(
                    f"Query '{query_name}' executed successfully - {len(result_dataframe)} rows"
                )
            else:
                print(f"Query '{query_name}' failed")

        workbook.save(output_file)
        print(f"Results saved to {output_file}")
