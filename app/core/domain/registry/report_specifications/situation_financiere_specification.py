from __future__ import annotations

# Local application imports
from app.core.domain.enums.report_category import ReportCategory
from app.core.domain.models.report_specification import ReportSpecification
from app.core.services.report_generation.generators.situation_financiere import (
    SituationFinanciereGenerator,
)

situation_financiere_specification: ReportSpecification = ReportSpecification(
    name="situation_financiere_des_programmes",
    display_name="Situation financière d'un programme",
    category=ReportCategory.HABITAT_RURAL,
    description=(
        "Situation financière détaillée d’un programme de logement, "
        "présentée par daira puis par commune. Comprend les engagements, "
        "les consommations et les restes."
    ),
    required_patterns={
        r"^Journal_paiements__Agence_[A-Z+]+_\d{2}\.\d{2}\.\d{4}_[0-9]+.xlsx$": "paiements",
        r"^Journal_décisions__Agence_[A-Z+]+_\d{2}\.\d{2}\.\d{4}_[0-9]+.xlsx$": "decisions",
    },
    example_files=[
        "Journal_paiements__Agence_WILAYA_JJ.MM.AAAA_CODE.xlsx",
        "Journal_décisions__Agence_WILAYA_JJ.MM.AAAA_CODE.xlsx",
    ],
    output_filename="situation_financiere_des_programmes_{wilaya}_{date}.xlsx",
    generator=SituationFinanciereGenerator,
    queries={
        "nb_aides_et_montants_inscrits_par_daira_et_commune": """
            SELECT
                d."Daira du projet",
                d."Commune du projet",
                COUNT(*) AS nb_aides_inscrites,
                COUNT(*) * {aid_value} AS montant_inscrits
            FROM decisions d
            WHERE d."Sous programme" = {programme}
            GROUP BY
                d."Daira du projet",
                d."Commune du projet"
        """,
        "consommations_cumulees_fin_annee_precedente": """
            SELECT
                p.Daira,
                p."Commune de projet",
                SUM(CASE WHEN p.T1 > 0 THEN 1 ELSE 0 END) +
                SUM(CASE WHEN p.C1 > 0 THEN 1 ELSE 0 END) +
                SUM(CASE WHEN p.N1 > 0 THEN 1 ELSE 0 END) AS t_1,
                SUM(CASE WHEN p.T2 > 0 THEN 1 ELSE 0 END) +
                SUM(CASE WHEN p.C2 > 0 THEN 1 ELSE 0 END) +
                SUM(CASE WHEN p.N2 > 0 THEN 1 ELSE 0 END) AS t_2,
                SUM(CASE WHEN p.T3 > 0 THEN 1 ELSE 0 END) AS t_3,
                (SUM(COALESCE(p.T1, 0)) + SUM(COALESCE(p.C1, 0)) + SUM(COALESCE(p.N1, 0)) +
                SUM(COALESCE(p.T2, 0)) + SUM(COALESCE(p.C2, 0)) + SUM(COALESCE(p.N2, 0)) +
                SUM(COALESCE(p.T3, 0))) * {aid_value} AS montant
            FROM paiements p
            WHERE p."Sous programme" = {programme}
            AND CAST(SUBSTRING("Date OV", 7, 4) AS INTEGER) < {year}
            GROUP BY
                p.Daira,
                p."Commune de projet"
        """,
        "consommations_annee_actuelle_jusqua_mois_actuel": """
            SELECT
                p.Daira,
                p."Commune de projet",
                SUM(CASE WHEN p.T1 > 0 THEN 1 ELSE 0 END) +
                SUM(CASE WHEN p.C1 > 0 THEN 1 ELSE 0 END) +
                SUM(CASE WHEN p.N1 > 0 THEN 1 ELSE 0 END) AS t_1,
                SUM(CASE WHEN p.T2 > 0 THEN 1 ELSE 0 END) +
                SUM(CASE WHEN p.C2 > 0 THEN 1 ELSE 0 END) +
                SUM(CASE WHEN p.N2 > 0 THEN 1 ELSE 0 END) AS t_2,
                SUM(CASE WHEN p.T3 > 0 THEN 1 ELSE 0 END) AS t_3,
                (SUM(COALESCE(p.T1, 0)) + SUM(COALESCE(p.C1, 0)) + SUM(COALESCE(p.N1, 0)) +
                SUM(COALESCE(p.T2, 0)) + SUM(COALESCE(p.C2, 0)) + SUM(COALESCE(p.N2, 0)) +
                SUM(COALESCE(p.T3, 0))) * {aid_value} AS montant
            FROM paiements p
            WHERE p."Sous programme" = {programme}
            AND CAST(SUBSTRING("Date OV", 7, 4) AS INTEGER) = {year}
            AND CAST(SUBSTRING("Date OV", 4, 2) AS INTEGER) <= {month} 
            GROUP BY
                p.Daira,
                p."Commune de projet"
        """,
    },
)
