from __future__ import annotations

# Local application imports
from app.core.domain.enums.report_category import ReportCategory
from app.core.domain.models.report_specification import (
    ReportSpecification,
    RequiredFile,
)
from app.core.services.report_generation_service.concrete_generators.activite_mensuelle import (
    ActiviteMensuelleGenerator,
)

activite_mensuelle_specification: ReportSpecification = ReportSpecification(
    name="activite_mensuelle",
    display_name="Rapport d'activité mensuelle",
    category=ReportCategory.HABITAT_RURAL,
    description=(
        "Comprend l’état d’exécution des tranches financières durant "
        "le mois et l’année spécifiés, en valeurs actuelles et cumulées, "
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
            ORDER BY s.display_order
        """,
        "lancements_mois": """
            SELECT 
                s.subprogram,
                COALESCE(data.count, 0) as count
            FROM subprograms s
            LEFT JOIN (
                SELECT
                    "Sous program",
                    COUNT(*) as count
                FROM paiements
                WHERE Tranche IN (
                    '20%  1 ERE TRANCHE',
                    '40%  Première Tranche',
                    '60%  Première Tranche',
                    '60%  1+2 EME TRANCHE',
                    '100%  Tranche totale',
                    '100%  1+2+3 EME TRANCHE'
                )
                AND "Date OV" LIKE '%/{month}/{year}'
                GROUP BY "Sous program"
            ) data ON s.subprogram = data."Sous program"
            ORDER BY s.display_order
        """,
        "lancements_cumul_annee": """
            SELECT 
                s.subprogram,
                COALESCE(data.count, 0) as count
            FROM subprograms s
            LEFT JOIN (
                SELECT
                    "Sous program",
                    COUNT(*) as count
                FROM paiements
                WHERE Tranche IN (
                    '20%  1 ERE TRANCHE',
                    '40%  Première Tranche',
                    '60%  Première Tranche',
                    '60%  1+2 EME TRANCHE',
                    '100%  Tranche totale',
                    '100%  1+2+3 EME TRANCHE'
                )
                AND CAST(SUBSTRING("Date OV", 4, 2) AS INTEGER) <= {month}
                AND "Date OV" LIKE '%/{year}'
                GROUP BY "Sous program"
            ) data ON s.subprogram = data."Sous program"
            ORDER BY s.display_order
        """,
        "livraisons_mois": """
            SELECT
                s.subprogram,
                COALESCE(data.count, 0) as count
            FROM subprograms s
            LEFT JOIN (
                SELECT
                    "Sous program",
                    COUNT(*) as count
                FROM paiements
                WHERE Tranche IN (
                    '40%  3 EME TRANCHE',
                    '40%  Deuxième Tranche',
                    '60%  Deuxième Tranche',
                    '80%  2+3 EME TRANCHE',
                    '100%  1+2+3 EME TRANCHE',
                    'Tranche complémentaire 2'
                )
                AND "Date OV" LIKE '%/{month}/{year}'
                GROUP BY "Sous program"
            ) data ON s.subprogram = data."Sous program"
            ORDER BY s.display_order
        """,
        "livraisons_cumul_annee": """
            SELECT 
                s.subprogram,
                COALESCE(data.count, 0) as count
            FROM subprograms s
            LEFT JOIN (
                SELECT
                    "Sous program",
                    COUNT(*) as count
                FROM paiements
                WHERE Tranche IN (
                    '40%  3 EME TRANCHE',
                    '40%  Deuxième Tranche',
                    '60%  Deuxième Tranche',
                    '80%  2+3 EME TRANCHE',
                    '100%  1+2+3 EME TRANCHE',
                    'Tranche complémentaire 2'
                )
                AND CAST(SUBSTRING("Date OV", 4, 2) AS INTEGER) <= {month}
                AND "Date OV" LIKE '%/{year}'
                GROUP BY "Sous program"
            ) data ON s.subprogram = data."Sous program"
            ORDER BY s.display_order
        """,
        "subprograms_situation": """
            SELECT 
                s.subprogram,
                s.aid_count,
                s.display_order
            FROM subprograms s
            ORDER BY s.display_order
        """,
        "acheves_derniere_tranche": """
            SELECT 
                s.subprogram,
                s.aid_count,
                COALESCE(data.count, 0) as acheves
            FROM subprograms s
            LEFT JOIN (
                SELECT
                    "Sous program",
                    COUNT(*) as count
                FROM paiements
                WHERE
                    N2 > 0
                    OR C2 > 0
                    OR T3 > 0
                GROUP BY "Sous program"
            ) data ON s.subprogram = data."Sous program"
            WHERE s.aid_count > 0
            ORDER BY s.display_order
        """,
        "en_cours_calculation": """
            SELECT 
                s.subprogram,
                s.aid_count,
                COALESCE(lances.count, 0) as lances_count,
                COALESCE(acheves.count, 0) as acheves_count,
                GREATEST(0, COALESCE(lances.count, 0) - COALESCE(acheves.count, 0)) as en_cours
            FROM subprograms s
            LEFT JOIN (
                SELECT
                    "Sous program",
                    COUNT(*) as count
                FROM paiements
                WHERE
                    N1 > 0
                    OR C1 > 0
                    OR T1 > 0
                GROUP BY "Sous program"
            ) lances ON s.subprogram = lances."Sous program"
            LEFT JOIN (
                SELECT
                    "Sous program",
                    COUNT(*) as count
                FROM paiements
                WHERE
                    N2 > 0
                    OR C2 > 0
                    OR T3 > 0
                GROUP BY "Sous program"
            ) acheves ON s.subprogram = acheves."Sous program"
            WHERE s.aid_count > 0
            ORDER BY s.display_order
        """,
        "non_lances_premiere_tranche": """
            SELECT 
                s.subprogram,
                s.aid_count,
                COALESCE(s.aid_count - data.count, s.aid_count) as non_lances
            FROM subprograms s
            LEFT JOIN (
                SELECT
                    "Sous program",
                    COUNT(*) as count
                FROM paiements
                WHERE
                    N1 > 0
                    OR C1 > 0
                    OR T1 > 0
                GROUP BY "Sous program"
            ) data ON s.subprogram = data."Sous program"
            WHERE s.aid_count > 0
            ORDER BY s.display_order
        """,
    },
)
