from __future__ import annotations

# Local application imports
from app.core.domain.enums.report_category import ReportCategory
from app.core.domain.models.report_specification import ReportSpecification
from app.core.services.report_generation.generators.situation_financiere import (
    SituationFinanciereGenerator,
)

situation_financiere_specification: ReportSpecification = ReportSpecification(
    name="situation_financiere_des_programmes",
    display_name="Situation financière des programmes",
    category=ReportCategory.HABITAT_RURAL,
    description=(
        "Situation financière détaillée des programmes de logements aidés "
        "par programme, daira et commune. Comprend les engagements, "
        "consommations et taux de réalisation."
    ),
    required_files={
        r"^Journal_paiements__Agence_[A-Z+]+_\d{2}\.\d{2}\.\d{4}_[0-9]+.xlsx$": "paiements",
        r"^Journal_decisions__Agence_[A-Z+]+_\d{2}\.\d{2}\.\d{4}_[0-9]+.xlsx$": "decisions",
    },
    queries={},
    output_filename="Situation_financière_des_programmes_{wilaya}_{date}.xlsx",
    generator=SituationFinanciereGenerator,
)
