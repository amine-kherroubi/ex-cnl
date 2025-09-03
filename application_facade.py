from __future__ import annotations
from typing import Any
import pandas as pd
from analytics_service import AnalyticsService
from config import ApplicationConfig
from data_repository import DuckDBRepository
from export_service import ExcelExportStrategy, ExportService
from query_service import QueryService


class ApplicationFacade:  # Facade Pattern
    def __init__(self, config: ApplicationConfig) -> None:
        self._config: ApplicationConfig = config

        # Dependency Injection Pattern
        self._repository: DuckDBRepository = DuckDBRepository()
        self._query_service: QueryService = QueryService()
        self._export_service: ExportService = ExportService(ExcelExportStrategy())
        self._analytics_service: AnalyticsService = AnalyticsService(
            self._repository, self._query_service
        )

    def run(self) -> None:
        try:
            # Load data
            self._load_data()

            # Show data summary if debug enabled
            if self._config.database.enable_debug:
                self._show_data_summary()

            # Generate reports
            results: dict[str, pd.DataFrame] = self._generate_reports()

            # Export results
            self._export_results(results)

        except Exception:
            raise
        finally:
            self._cleanup()

    def _load_data(self) -> None:
        self._repository.load_data(self._config.input_file)

    def _show_data_summary(self) -> None:
        summary: dict[str, Any] = self._repository.get_data_summary()

        print("Data Summary:")
        print(f"Total records: {summary.get('total_records')}")

        print(f"\nTable description:")
        print(summary.get("table_description"))

        print("\nSample data:")
        print(summary["sample_data"])

    def _generate_reports(self) -> dict[str, pd.DataFrame]:
        return self._analytics_service.generate_reports()

    def _export_results(self, results: dict[str, pd.DataFrame]) -> None:
        if results:
            self._export_service.export_results(results, self._config.output_file)

    def _cleanup(self) -> None:
        self._repository.close()
