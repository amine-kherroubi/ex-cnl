# Standard library imports
from typing import Final

# Local application imports
from app.core.domain.enums.report_category import ReportCategory
from app.core.domain.models.report_specification import (
    ReportSpecification,
    RequiredFile,
)
from app.core.services.report_generation_service.concrete_generators.situation_financiere import (
    SituationFinanciereGenerator,
)

situation_par_sous_programme_specification: Final[ReportSpecification] = ReportSpecification(
    name="situation_par_sous_programme",
    display_name="Situation financière par sous-programme",
    category=ReportCategory.HABITAT_RURAL,
    description=(
        "Présente la situation financière par sous-programme "
        "(tous les sous-programmes). Inclut les engagements, les consommations, "
        "les cumuls et les restes relatifs à chaque sous-programme."
    ),
    required_files=[
        RequiredFile(
            name="Journal des paiements",
            pattern=r"^Journal_paiements__Agence_[A-Z+-_]+_\d{2}\.\d{2}\.\d{4}_[0-9]+.xlsx$",
            readable_pattern="Journal_paiements__Agence_WILAYA_JJ.MM.AAAA_CODE.xlsx",
            table_name="paiements",
        ),
        RequiredFile(
            name="Journal des décisions",
            pattern=r"^Journal_décisions__Agence_[A-Z+-_]+_\d{2}\.\d{2}\.\d{4}_[0-9]+.xlsx$",
            readable_pattern="Journal_décisions__Agence_WILAYA_JJ.MM.AAAA_CODE.xlsx",
            table_name="decisions",
        ),
    ],
    output_filename="situation_financiere_{wilaya}_{date}.xlsx",
    generator=SituationFinanciereGenerator,
    queries={
        "subprograms": """
            SELECT s.subprogram
            FROM subprograms s
        """,
        "nb_aides_et_montants_inscrits_par_sous_programme": """
            WITH decision_summary AS (
                SELECT
                    d."Sous programme",
                    d."Code décision",
                    SUM(d."Financier") AS net_amount,
                    SUM(d."Physique") AS decsision_value
                FROM decisions d
                GROUP BY
                    d."Sous programme",
                    d."Code décision"
                HAVING SUM(d."Physique") > 0
            )
            SELECT
                ds."Sous programme",
                COUNT(*) AS nb_aides_inscrites,
                SUM(ds.net_amount) AS montant_inscrits
            FROM decision_summary ds
            GROUP BY
                ds."Sous programme"
        """,
        "consommations_cumulees_fin_annee_precedente": """
            WITH payment_summary AS (
                SELECT
                    p."Sous programme",
                    p."Code OV",
                    SUM(COALESCE(p.T1, 0)) AS net_t1,
                    SUM(COALESCE(p.C1, 0)) AS net_c1,
                    SUM(COALESCE(p.N1, 0)) AS net_n1,
                    SUM(COALESCE(p.T2, 0)) AS net_t2,
                    SUM(COALESCE(p.C2, 0)) AS net_c2,
                    SUM(COALESCE(p.N2, 0)) AS net_n2,
                    SUM(COALESCE(p.T3, 0)) AS net_t3,
                    SUM(p."valeur physique") AS decision_value
                FROM paiements p
                AND CAST(SUBSTRING("Date OV", 7, 4) AS INTEGER) < {year}
                GROUP BY
                    p."Sous programme",
                    p."Code OV"
                HAVING decision_value > 0
            )
            SELECT
                ps."Sous programme",
                SUM(CASE WHEN (ps.net_t1 + ps.net_c1 + ps.net_n1) > 0 THEN 1 ELSE 0 END) AS t_1,
                SUM(CASE WHEN (ps.net_t2 + ps.net_c2 + ps.net_n2) > 0 THEN 1 ELSE 0 END) AS t_2,
                SUM(CASE WHEN ps.net_t3 > 0 THEN 1 ELSE 0 END) AS t_3,
                SUM(ps.net_t1 + ps.net_c1 + ps.net_n1 + ps.net_t2 + ps.net_c2 + ps.net_n2 + ps.net_t3) AS montant
            FROM payment_summary ps
            GROUP BY
                ps."Sous programme"
        """,
        "consommations_annee_actuelle_jusqua_mois_actuel": """
            WITH payment_summary AS (
                SELECT
                    p."Sous programme",
                    p."Code OV",
                    SUM(COALESCE(p.T1, 0)) AS net_t1,
                    SUM(COALESCE(p.C1, 0)) AS net_c1,
                    SUM(COALESCE(p.N1, 0)) AS net_n1,
                    SUM(COALESCE(p.T2, 0)) AS net_t2,
                    SUM(COALESCE(p.C2, 0)) AS net_c2,
                    SUM(COALESCE(p.N2, 0)) AS net_n2,
                    SUM(COALESCE(p.T3, 0)) AS net_t3,
                    SUM(p."valeur physique") AS decision_value
                FROM paiements p
                AND CAST(SUBSTRING("Date OV", 7, 4) AS INTEGER) = {year}
                AND CAST(SUBSTRING("Date OV", 4, 2) AS INTEGER) <= {month}
                GROUP BY
                    p."Sous programme",
                    p."Code OV"
                HAVING decision_value > 0
            )
            SELECT
                ps."Sous programme",
                SUM(CASE WHEN (ps.net_t1 + ps.net_c1 + ps.net_n1) > 0 THEN 1 ELSE 0 END) AS t_1,
                SUM(CASE WHEN (ps.net_t2 + ps.net_c2 + ps.net_n2) > 0 THEN 1 ELSE 0 END) AS t_2,
                SUM(CASE WHEN ps.net_t3 > 0 THEN 1 ELSE 0 END) AS t_3,
                SUM(ps.net_t1 + ps.net_c1 + ps.net_n1 + ps.net_t2 + ps.net_c2 + ps.net_n2 + ps.net_t3) AS montant
            FROM payment_summary ps
            GROUP BY
                ps."Sous programme"
        """,
    },
)
