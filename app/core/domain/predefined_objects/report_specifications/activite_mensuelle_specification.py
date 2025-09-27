from __future__ import annotations

# Standard library imports
from typing import Final

# Local application imports
from app.core.domain.enums.report_category import ReportCategory
from app.core.domain.models.report_specification import (
    ReportSpecification,
    RequiredFile,
)
from app.core.services.report_generation_service.concrete_generators.activite_mensuelle import (
    ActiviteMensuelleGenerator,
)

TRANCHES_DE_LANCEMENT: Final[set[str]] = {
    "N1        ",
    "C1        ",
    "T1        ",
    "T1, T2    ",
}

TRANCHES_DE_LIVRAISON: Final[set[str]] = {
    "N1, N2    ",
    "N2        ",
    "T2, T3    ",
    "T1, T2, T3",
    "T3        ",
    "C2        ",
}

TRANCHES_INTERMEDIARES: Final[set[str]] = {
    "T2        ",
    "          ",  # Empty
}

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
            SELECT 
                s.subprogram,
                COALESCE(data.count, 0) as count
            FROM subprograms s
            LEFT JOIN (
                SELECT
                    "Sous programme",
                    COUNT(*) as count
                FROM paiements
                WHERE "Tranche du rapport" IN ({', '.join(f"'{tranche}'" for tranche in TRANCHES_DE_LANCEMENT)})
                AND "Date OV" LIKE '%/{{month}}/{{year}}'
                AND "valeur physique" > 0
                GROUP BY "Sous programme"
            ) data ON s.subprogram = data."Sous programme"
        """,
        "lancements_cumul_annee": f"""
            SELECT 
                s.subprogram,
                COALESCE(data.count, 0) as count
            FROM subprograms s
            LEFT JOIN (
                SELECT
                    "Sous programme",
                    COUNT(*) as count
                FROM paiements
                WHERE "Tranche du rapport" IN ({', '.join(f"'{tranche}'" for tranche in TRANCHES_DE_LANCEMENT)})
                AND CAST(SUBSTRING("Date OV", 4, 2) AS INTEGER) <= {{month}}
                AND "Date OV" LIKE '%/{{year}}'
                AND "valeur physique" > 0
                GROUP BY "Sous programme"
            ) data ON s.subprogram = data."Sous programme"
        """,
        "livraisons_mois": f"""
            SELECT
                s.subprogram,
                COALESCE(data.count, 0) as count
            FROM subprograms s
            LEFT JOIN (
                SELECT
                    "Sous programme",
                    COUNT(*) as count
                FROM paiements
                WHERE "Tranche du rapport" IN ({', '.join(f"'{tranche}'" for tranche in TRANCHES_DE_LIVRAISON)})
                AND "Date OV" LIKE '%/{{month}}/{{year}}'
                AND "valeur physique" > 0
                GROUP BY "Sous programme"
            ) data ON s.subprogram = data."Sous programme"
        """,
        "livraisons_cumul_annee": f"""
            SELECT 
                s.subprogram,
                COALESCE(data.count, 0) as count
            FROM subprograms s
            LEFT JOIN (
                SELECT
                    "Sous programme",
                    COUNT(*) as count
                FROM paiements
                WHERE "Tranche du rapport" IN ({', '.join(f"'{tranche}'" for tranche in TRANCHES_DE_LIVRAISON)})
                AND CAST(SUBSTRING("Date OV", 4, 2) AS INTEGER) <= {{month}}
                AND "Date OV" LIKE '%/{{year}}'
                AND "valeur physique" > 0
                GROUP BY "Sous programme"
            ) data ON s.subprogram = data."Sous programme"
        """,
        "subprograms_situation": """
            SELECT 
                s.subprogram,
                s.aid_count,
            FROM subprograms s
        """,
        "acheves_derniere_tranche": f"""
            SELECT 
                s.subprogram,
                s.aid_count,
                COALESCE(data.count, 0) as acheves
            FROM subprograms s
            LEFT JOIN (
                SELECT
                    "Sous programme",
                    COUNT(*) as count
                FROM paiements
                WHERE "Tranche du rapport" IN ({', '.join(f"'{tranche}'" for tranche in TRANCHES_DE_LIVRAISON)})
                AND "valeur physique" > 0
                GROUP BY "Sous programme"
            ) data ON s.subprogram = data."Sous programme"
            WHERE s.aid_count > 0
        """,
        "en_cours_calculation": f"""
            SELECT 
                s.subprogram,
                s.aid_count,
                COALESCE(lances.count, 0) as lances_count,
                COALESCE(acheves.count, 0) as acheves_count,
                GREATEST(0, COALESCE(lances.count, 0) - COALESCE(acheves.count, 0)) as en_cours
            FROM subprograms s
            LEFT JOIN (
                SELECT
                    "Sous programme",
                    COUNT(*) as count
                FROM paiements
                WHERE "Tranche du rapport" IN ({', '.join(f"'{tranche}'" for tranche in TRANCHES_DE_LANCEMENT)})
                AND "valeur physique" > 0
                GROUP BY "Sous programme"
            ) lances ON s.subprogram = lances."Sous programme"
            LEFT JOIN (
                SELECT
                    "Sous programme",
                    COUNT(*) as count
                FROM paiements
                WHERE "Tranche du rapport" IN ({', '.join(f"'{tranche}'" for tranche in TRANCHES_DE_LIVRAISON)})
                GROUP BY "Sous programme"
            ) acheves ON s.subprogram = acheves."Sous programme"
            WHERE s.aid_count > 0
        """,
        "non_lances_premiere_tranche": f"""
            SELECT 
                s.subprogram,
                s.aid_count,
                COALESCE(s.aid_count - data.count, s.aid_count) as non_lances
            FROM subprograms s
            LEFT JOIN (
                SELECT
                    "Sous programme",
                    COUNT(*) as count
                FROM paiements
                WHERE "Tranche du rapport" IN ({', '.join(f"'{tranche}'" for tranche in TRANCHES_DE_LANCEMENT)})
                AND "valeur physique" > 0
                GROUP BY "Sous programme"
            ) data ON s.subprogram = data."Sous programme"
            WHERE s.aid_count > 0
        """,
    },
)
