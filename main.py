from __future__ import annotations
from queries import get_queries
from excel import ExcelExporter
from database import Database


def main() -> None:
    input_filename: str = (
        "Liste_OVs_Agence_TIZIOUZOU_17.09.2024_7284743114531606447.xlsx"
    )
    output_filename: str = "resultats_requetes.xlsx"

    try:
        print("Setting up database...")
        database: Database = Database()
        database.setup_from_excel(input_filename)
        database.debug_data_structure()
        analytical_queries: dict[str, str] = get_queries()
        print("\nExecuting queries and saving results...")
        excel_exporter: ExcelExporter = ExcelExporter()
        excel_exporter.save_results_to_excel(
            analytical_queries,
            database,
            output_filename,
        )
        database.close()
        print(f"Results saved to {output_filename}")

    except Exception as e:
        print(f"Error in main execution: {e}")
        raise


if __name__ == "__main__":
    main()
