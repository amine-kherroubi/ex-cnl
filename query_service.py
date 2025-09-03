from __future__ import annotations
from typing import Final


class QueryService:  # Service Pattern
    def __init__(self) -> None:
        pass

    @property
    def available_queries(self) -> dict[str, str]:
        return QUERY_DEFINITIONS

    def get_query(self, query_name: str) -> str:
        if query_name not in QUERY_DEFINITIONS:
            available: str = ", ".join(QUERY_DEFINITIONS.keys())
            raise ValueError(f"Query '{query_name}' not found. Available: {available}")

        return QUERY_DEFINITIONS[query_name]

    def validate_query(self, query: str) -> bool:
        # Basic SQL injection protection
        dangerous_keywords: list[str] = [
            "DROP",
            "DELETE",
            "TRUNCATE",
            "INSERT",
            "UPDATE",
            "ALTER",
        ]

        return not any(keyword in query.upper() for keyword in dangerous_keywords)


QUERY_DEFINITIONS: Final[dict[str, str]] = {
    "overview_by_commune": """
        SELECT
            Commune,
            COUNT(*) as total_ovs,
            SUM(CASE WHEN "Annulé?" = 'non' THEN 1 ELSE 0 END) as active_ovs,
            SUM(CASE WHEN "Annulé?" = 'oui' THEN 1 ELSE 0 END) as cancelled_ovs,
            SUM(CASE WHEN "Annulé?" = 'non' THEN Montant ELSE 0 END) as total_active_amount,
            AVG(CASE WHEN "Annulé?" = 'non' THEN Montant ELSE NULL END) as avg_amount_per_ov
        FROM ovs
        WHERE Commune IS NOT NULL
        GROUP BY Commune
        ORDER BY total_active_amount DESC
    """,
    "program_summary": """
        SELECT
            Programme,
            "Sous programme",
            COUNT(*) as total_ovs,
            SUM(CASE WHEN "Annulé?" = 'non' THEN 1 ELSE 0 END) as active_ovs,
            SUM(CASE WHEN "Annulé?" = 'non' THEN Montant ELSE 0 END) as total_amount,
            COUNT(DISTINCT Commune) as communes_served
        FROM ovs
        WHERE Programme IS NOT NULL
        GROUP BY Programme, "Sous programme"
        ORDER BY total_amount DESC
    """,
    "top_beneficiaries": """
        SELECT
            Nom,
            Prénom,
            Commune,
            COUNT(*) as number_of_ovs,
            SUM(CASE WHEN "Annulé?" = 'non' THEN Montant ELSE 0 END) as total_amount
        FROM ovs
        WHERE "Annulé?" = 'non' AND Nom IS NOT NULL
        GROUP BY Nom, Prénom, Commune
        HAVING SUM(CASE WHEN "Annulé?" = 'non' THEN Montant ELSE 0 END) > 0
        ORDER BY total_amount DESC
        LIMIT 50
    """,
    "tranche_analysis": """
        SELECT
            Tranche,
            COUNT(*) as count_ovs,
            SUM(CASE WHEN "Annulé?" = 'non' THEN Montant ELSE 0 END) as total_amount,
            COUNT(DISTINCT Commune) as communes_involved
        FROM ovs
        WHERE Tranche IS NOT NULL
        GROUP BY Tranche
        ORDER BY total_amount DESC
    """,
    "monthly_activity": """
        SELECT
            SUBSTR("Date OV", 4, 7) as month_year,
            COUNT(*) as total_ovs,
            SUM(CASE WHEN "Annulé?" = 'non' THEN 1 ELSE 0 END) as active_ovs,
            SUM(CASE WHEN "Annulé?" = 'non' THEN Montant ELSE 0 END) as total_amount
        FROM ovs
        WHERE "Date OV" IS NOT NULL AND LENGTH("Date OV") >= 10
        GROUP BY SUBSTR("Date OV", 4, 7)
        ORDER BY month_year DESC
        LIMIT 24
    """,
    "construction_types": """
        SELECT
            "Type de construction",
            COUNT(*) as total_ovs,
            SUM(CASE WHEN "Annulé?" = 'non' THEN Montant ELSE 0 END) as total_amount,
            COUNT(DISTINCT Commune) as communes_count
        FROM ovs
        WHERE "Type de construction" IS NOT NULL
        GROUP BY "Type de construction"
        ORDER BY total_amount DESC
    """,
    "bank_agencies": """
        SELECT
            "Agence bancaire",
            COUNT(*) as total_ovs,
            SUM(CASE WHEN "Annulé?" = 'non' THEN Montant ELSE 0 END) as total_amount,
            COUNT(DISTINCT Commune) as communes_served
        FROM ovs
        WHERE "Agence bancaire" IS NOT NULL
        GROUP BY "Agence bancaire"
        ORDER BY total_amount DESC
    """,
}
