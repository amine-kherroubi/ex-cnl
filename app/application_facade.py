from __future__ import annotations
from typing import Any
import pandas
from utils.config import ApplicationConfig
from data.data_repository import DuckDBRepository


class ApplicationFacade(object):  # Facade pattern
    def __init__(self, config: ApplicationConfig) -> None:
        self._config: ApplicationConfig = config

        # Dependency injection pattern
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
            results: dict[str, pandas.DataFrame] = self._generate_reports()

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

    def _generate_reports(self) -> dict[str, pandas.DataFrame]:
        return self._analytics_service.generate_reports()

    def _export_results(self, results: dict[str, pandas.DataFrame]) -> None:
        if results:
            self._export_service.export_results(results, self._config.output_file)

    def _cleanup(self) -> None:
        self._repository.close()
