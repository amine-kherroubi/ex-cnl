# Standard library imports
from typing import Final

# Local application imports
from app.core.domain.enums.report_category import ReportCategory
from app.core.domain.models.report_specification import (
    ReportSpecification,
    RequiredFile,
)
from app.core.domain.predefined_objects.tranches import (
    TRANCHES_DE_LANCEMENT,
    TRANCHES_DE_LIVRAISON,
)
from app.core.services.report_generation_service.concrete_generators.activite_mensuelle import (
    ActiviteMensuelleGenerator,
)


activite_mensuelle_specification: Final[ReportSpecification] = ReportSpecification(
    name="activite_mensuelle",
    display_name="Rapport d'activité mensuelle",
    category=ReportCategory.HABITAT_RURAL,
    description=(
        "Comprend l'état d'exécution des tranches financières durant "
        "le mois et l'année spécifiés, en valeurs actuelles et cumulées, "
        "ainsi que la situation des sous-programmes "
        "en aides achevées, en cours ou non encore lancés."
    ),
    required_files=[
        RequiredFile(
            name="Journal des paiements",
            pattern=r"^Journal_paiements__Agence_[A-Z+-_]+_\d{2}\.\d{2}\.\d{4}_[0-9]+.xlsx$",
            readable_pattern="Journal_paiements__Agence_WILAYA_JJ.MM.AAAA_CODE.xlsx",
            table_name="paiements",
        )
    ],
    output_filename="activite_mensuelle_{wilaya}_{date}.xlsx",
    generator=ActiviteMensuelleGenerator,
    queries={
        "subprograms": """
            SELECT s.subprogram
            FROM subprograms s
        """,
        "lancements_mois": f"""
            WITH payment_summary AS (
                SELECT
                    p."Sous programme",
                    p."Code OV",
                    SUM(p."valeur physique") AS decision_value
                FROM paiements p
                WHERE p."Tranche" IN ({', '.join(f"'{tranche}'" for tranche in TRANCHES_DE_LANCEMENT)})
                AND (
                    p."Date OV" LIKE '%/{{month}}/{{year}}'
                    OR p."Date OV" LIKE '%/0{{month}}/{{year}}'
                )
                GROUP BY
                    p."Sous programme",
                    p."Code OV"
                HAVING decision_value > 0
            )
            SELECT
                s.subprogram,
                COALESCE(data.count, 0) as count
            FROM subprograms s
            LEFT JOIN (
                SELECT
                    ps."Sous programme",
                    COUNT(*) as count
                FROM payment_summary ps
                GROUP BY ps."Sous programme"
            ) data ON s.subprogram = data."Sous programme"
        """,
        "lancements_cumul_annee": f"""
            WITH payment_summary AS (
                SELECT
                    p."Sous programme",
                    p."Code OV",
                    SUM(p."valeur physique") AS decision_value
                FROM paiements p
                WHERE p."Tranche" IN ({', '.join(f"'{tranche}'" for tranche in TRANCHES_DE_LANCEMENT)})
                AND CAST(SUBSTRING(p."Date OV", 4, 2) AS INTEGER) <= {{month}}
                AND p."Date OV" LIKE '%/{{year}}'
                GROUP BY
                    p."Sous programme",
                    p."Code OV"
                HAVING decision_value > 0
            )
            SELECT 
                s.subprogram,
                COALESCE(data.count, 0) as count
            FROM subprograms s
            LEFT JOIN (
                SELECT
                    ps."Sous programme",
                    COUNT(*) as count
                FROM payment_summary ps
                GROUP BY ps."Sous programme"
            ) data ON s.subprogram = data."Sous programme"
        """,
        "livraisons_mois": f"""
            WITH payment_summary AS (
                SELECT
                    p."Sous programme",
                    p."Code OV",
                    SUM(p."valeur physique") AS decision_value
                FROM paiements p
                WHERE p."Tranche" IN ({', '.join(f"'{tranche}'" for tranche in TRANCHES_DE_LIVRAISON)})
                AND (
                    p."Date OV" LIKE '%/{{month}}/{{year}}'
                    OR p."Date OV" LIKE '%/0{{month}}/{{year}}'
                )
                GROUP BY
                    p."Sous programme",
                    p."Code OV"
                HAVING decision_value > 0
            )
            SELECT
                s.subprogram,
                COALESCE(data.count, 0) as count
            FROM subprograms s
            LEFT JOIN (
                SELECT
                    ps."Sous programme",
                    COUNT(*) as count
                FROM payment_summary ps
                GROUP BY ps."Sous programme"
            ) data ON s.subprogram = data."Sous programme"
        """,
        "livraisons_cumul_annee": f"""
            WITH payment_summary AS (
                SELECT
                    p."Sous programme",
                    p."Code OV",
                    SUM(p."valeur physique") AS decision_value
                FROM paiements p
                WHERE p."Tranche" IN ({', '.join(f"'{tranche}'" for tranche in TRANCHES_DE_LIVRAISON)})
                AND CAST(SUBSTRING(p."Date OV", 4, 2) AS INTEGER) <= {{month}}
                AND p."Date OV" LIKE '%/{{year}}'
                GROUP BY
                    p."Sous programme",
                    p."Code OV"
                HAVING decision_value > 0
            )
            SELECT 
                s.subprogram,
                COALESCE(data.count, 0) as count
            FROM subprograms s
            LEFT JOIN (
                SELECT
                    ps."Sous programme",
                    COUNT(*) as count
                FROM payment_summary ps
                GROUP BY ps."Sous programme"
            ) data ON s.subprogram = data."Sous programme"
        """,
        "subprograms_situation": """
            SELECT 
                s.subprogram,
                s.aid_count,
            FROM subprograms s
        """,
        "acheves_derniere_tranche": f"""
            WITH payment_summary AS (
                SELECT
                    p."Sous programme",
                    p."Code OV",
                    SUM(p."valeur physique") AS decision_value
                FROM paiements p
                WHERE p."Tranche" IN ({', '.join(f"'{tranche}'" for tranche in TRANCHES_DE_LIVRAISON)})
                GROUP BY
                    p."Sous programme",
                    p."Code OV"
                HAVING decision_value > 0
            )
            SELECT 
                s.subprogram,
                COALESCE(data.count, 0) as acheves
            FROM subprograms s
            LEFT JOIN (
                SELECT
                    ps."Sous programme",
                    COUNT(*) as count
                FROM payment_summary ps
                GROUP BY ps."Sous programme"
            ) data ON s.subprogram = data."Sous programme"
        """,
        "en_cours_calculation": f"""
            WITH lances_summary AS (
                SELECT
                    p."Sous programme",
                    p."Code OV",
                    SUM(p."valeur physique") AS decision_value
                FROM paiements p
                WHERE p."Tranche" IN ({', '.join(f"'{tranche}'" for tranche in TRANCHES_DE_LANCEMENT)})
                GROUP BY
                    p."Sous programme",
                    p."Code OV"
                HAVING decision_value > 0
            ),
            acheves_summary AS (
                SELECT
                    p."Sous programme",
                    p."Code OV",
                    SUM(p."valeur physique") AS decision_value
                FROM paiements p
                WHERE p."Tranche" IN ({', '.join(f"'{tranche}'" for tranche in TRANCHES_DE_LIVRAISON)})
                GROUP BY
                    p."Sous programme",
                    p."Code OV"
                HAVING decision_value > 0
            )
            SELECT
                s.subprogram,
                COALESCE(lances.count, 0) as lances_count,
                COALESCE(acheves.count, 0) as acheves_count,
                GREATEST(0, COALESCE(lances.count, 0) - COALESCE(acheves.count, 0)) as en_cours
            FROM subprograms s
            LEFT JOIN (
                SELECT
                    ls."Sous programme",
                    COUNT(*) as count
                FROM lances_summary ls
                GROUP BY ls."Sous programme"
            ) lances ON s.subprogram = lances."Sous programme"
            LEFT JOIN (
                SELECT
                    as_."Sous programme",
                    COUNT(*) as count
                FROM acheves_summary as_
                GROUP BY as_."Sous programme"
            ) acheves ON s.subprogram = acheves."Sous programme"
        """,
    },
)
