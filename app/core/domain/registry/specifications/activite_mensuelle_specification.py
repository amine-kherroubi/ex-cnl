from __future__ import annotations

# Local application imports
from app.core.domain.enums.report_category import ReportCategory
from app.core.domain.enums.space_time import Periodicity
from app.core.domain.models.report_specification import ReportSpecification
from app.core.services.report_generation.generators.activite_mensuelle import (
    ActiviteMensuelleGenerator,
)


activite_mensuelle_specification: ReportSpecification = ReportSpecification(
    name="activite_mensuelle_par_programme",
    display_name="Activité mensuelle",
    category=ReportCategory.HABITAT_RURAL,
    periodicity=Periodicity.MONTHLY,
    description=(
        "Report de suivi mensuel des activités par programme, "
        "renseigné par la BNH (ex-CNL). Comprend les lancements et livraisons "
        "ainsi que la situation globale des programmes."
    ),
    required_files={
        r"^Journal_paiements__Agence_[A-Z+]+_\d{2}\.\d{2}\.\d{4}_[0-9]+.xlsx$": "paiements",
    },
    queries={
        "programmes": """
                    SELECT programme
                    FROM programmes
                    ORDER BY display_order
                """,
        # Lancements du mois - projets ayant reçu leur première tranche
        "lancements_mois": """
                    SELECT 
                        p.programme,
                        COALESCE(data.count, 0) as count
                    FROM programmes p
                    LEFT JOIN (
                        SELECT
                            "Sous programme",
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
                            AND "Date OV" LIKE '%/{month_number:02d}/{year}'
                        GROUP BY "Sous programme"
                    ) data ON p.programme = data."Sous programme"
                    ORDER BY p.display_order
                """,
        # Cumul des lancements depuis le début de l'année
        "lancements_cumul_annee": """
                    SELECT 
                        p.programme,
                        COALESCE(data.count, 0) as count
                    FROM programmes p
                    LEFT JOIN (
                        SELECT
                            "Sous programme",
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
                            AND CAST(SUBSTRING("Date OV", POSITION('/' IN "Date OV") + 1, 2) AS INTEGER) <= {month_number}
                            AND "Date OV" LIKE '%/{year}'
                        GROUP BY "Sous programme"
                    ) data ON p.programme = data."Sous programme"
                    ORDER BY p.display_order
                """,
        # Livraisons du mois - projets ayant reçu leur dernière tranche
        "livraisons_mois": """
                    SELECT
                        p.programme,
                        COALESCE(data.count, 0) as count
                    FROM programmes p
                    LEFT JOIN (
                        SELECT
                            "Sous programme",
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
                            AND "Date OV" LIKE '%/{month_number:02d}/{year}'
                        GROUP BY "Sous programme"
                    ) data ON p.programme = data."Sous programme"
                    ORDER BY p.display_order
                """,
        # Cumul des livraisons depuis le début de l'année
        "livraisons_cumul_annee": """
                    SELECT 
                        p.programme,
                        COALESCE(data.count, 0) as count
                    FROM programmes p
                    LEFT JOIN (
                        SELECT
                            "Sous programme",
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
                            AND CAST(SUBSTRING("Date OV", POSITION('/' IN "Date OV") + 1, 2) AS INTEGER) <= {month_number}
                            AND "Date OV" LIKE '%/{year}'
                        GROUP BY "Sous programme"
                    ) data ON p.programme = data."Sous programme"
                    ORDER BY p.display_order
                """,
        # Programmes avec leur consistance (nombre d'aides planifiéss)
        "programmes_situation": """
                    SELECT 
                        programme,
                        consistance,
                        display_order
                    FROM programmes
                    ORDER BY display_order
                """,
        # Projets achevés - ayant reçu la dernière tranche de paiement
        "acheves_derniere_tranche": """
                    SELECT 
                        p.programme,
                        p.consistance,
                        COALESCE(data.count, 0) as acheves
                    FROM programmes p
                    LEFT JOIN (
                        SELECT
                            "Sous programme",
                            COUNT(*) as count
                        FROM paiements
                        WHERE N2 > 0
                            OR C2 > 0
                            OR T3 > 0
                        GROUP BY "Sous programme"
                    ) data ON p.programme = data."Sous programme"
                    WHERE p.consistance > 0
                    ORDER BY p.display_order
                """,
        # Projets en cours (lancés mais non achevés)
        "en_cours_calculation": """
                    SELECT 
                        p.programme,
                        p.consistance,
                        COALESCE(lances.count, 0) as lances_count,
                        COALESCE(acheves.count, 0) as acheves_count,
                        GREATEST(0, COALESCE(lances.count, 0) - COALESCE(acheves.count, 0)) as en_cours
                    FROM programmes p
                    LEFT JOIN (
                        SELECT
                            "Sous programme",
                            COUNT(*) as count
                        FROM paiements
                        WHERE N1 > 0
                            OR C1 > 0
                            OR T1 > 0
                        GROUP BY "Sous programme"
                    ) lances ON p.programme = lances."Sous programme"
                    LEFT JOIN (
                        SELECT
                            "Sous programme",
                            COUNT(*) as count
                        FROM paiements
                        WHERE N2 > 0
                            OR C2 > 0
                            OR T3 > 0
                        GROUP BY "Sous programme"
                    ) acheves ON p.programme = acheves."Sous programme"
                    WHERE p.consistance > 0
                    ORDER BY p.display_order
                """,
        # Non encore lancés (consistance - premières tranches payées)
        "non_lances_premiere_tranche": """
                    SELECT 
                        p.programme,
                        p.consistance,
                        COALESCE(p.consistance - data.count, p.consistance) as non_lances
                    FROM programmes p
                    LEFT JOIN (
                        SELECT
                            "Sous programme",
                            COUNT(*) as count
                        FROM paiements
                        WHERE N1 > 0
                            OR C1 > 0
                            OR T1 > 0
                        GROUP BY "Sous programme"
                    ) data ON p.programme = data."Sous programme"
                    WHERE p.consistance > 0
                    ORDER BY p.display_order
                """,
    },
    output_filename="Activité_mensuelle_par_programme_{wilaya}_{date}.xlsx",
    generator=ActiviteMensuelleGenerator,
)
