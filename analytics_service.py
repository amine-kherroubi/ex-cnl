from __future__ import annotations
import pandas as pd
from data_repository import DataRepository
from query_service import QueryService


class AnalyticsService:  # Service Pattern
    def __init__(self, repository: DataRepository, query_service: QueryService) -> None:
        self._repository: DataRepository = repository
        self._query_service: QueryService = query_service

    def generate_reports(
        self, query_names: list[str] | None = None
    ) -> dict[str, pd.DataFrame]:
        if query_names is None:
            query_names = list(self._query_service.available_queries.keys())

        results: dict[str, pd.DataFrame] = {}

        for query_name in query_names:
            try:
                query: str = self._query_service.get_query(query_name)

                if not self._query_service.validate_query(query):
                    continue

                result: pd.DataFrame = self._repository.execute_query(query)
                results[query_name] = result

            except Exception:
                # Skip failed queries
                continue

        return results
