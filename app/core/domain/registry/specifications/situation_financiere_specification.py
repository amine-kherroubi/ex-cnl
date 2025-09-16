from __future__ import annotations

# Local application imports
from app.core.domain.enums.report_category import ReportCategory
from app.core.domain.enums.space_time import Periodicity
from app.core.domain.models.report_specification import ReportSpecification
from app.core.services.report_generation.generators.situation_financiere import (
    SituationFinanciereGenerator,
)

situation_financiere_specification: ReportSpecification = ReportSpecification(
    name="situation_financiere_des_programmes",
    display_name="Situation financière des programmes",
    category=ReportCategory.HABITAT_RURAL,
    periodicity=Periodicity.MONTHLY,
    description=(
        "Situation financière détaillée des programmes de logements aidés "
        "par programme, daira et commune. Comprend les engagements, "
        "consommations et taux de réalisation."
    ),
    required_files={
        r"^Journal_paiements__Agence_[A-Z+]+_\d{2}\.\d{2}\.\d{4}_[0-9]+.xlsx$": "paiements",
        r"^Journal_decisions__Agence_[A-Z+]+_\d{2}\.\d{2}\.\d{4}_[0-9]+.xlsx$": "decisions",
    },
    queries={
        # Données agrégées par daira et commune
        "data_by_daira_commune": """
                    SELECT 
                        COALESCE(d."Daira du projet", p."Daira") as daira,
                        COALESCE(d."Commune", p."Commune") as commune,
                        COUNT(DISTINCT d."Code déc") as nb_aides_inscrits,
                        COUNT(DISTINCT CASE WHEN p."N° d'ordre" IS NOT NULL THEN d."Code déc" END) as nb_aides_bnh,
                        SUM(CASE WHEN p."N° d'ordre" IS NOT NULL THEN COALESCE(d."Financier", 0) ELSE 0 END) as montants_inscrits,
                        COUNT(DISTINCT CASE WHEN p."T1" > 0 OR p."N1" > 0 OR p."C1" > 0 THEN p."N° d'ordre" END) as nb_aides_lances,
                        SUM(CASE WHEN p."T1" > 0 OR p."N1" > 0 OR p."C1" > 0 THEN COALESCE(p."T1", 0) + COALESCE(p."N1", 0) + COALESCE(p."C1", 0) ELSE 0 END) as montants_decrits,
                        COUNT(DISTINCT CASE WHEN d."Type" = 'Décision' THEN d."Code déc" END) as nb_aides_mdv,
                        SUM(CASE WHEN d."Type" = 'Décision' THEN COALESCE(d."Financier", 0) ELSE 0 END) as montants_mdv,
                        COUNT(DISTINCT CASE 
                            WHEN CAST(SUBSTRING(p."Date OV", -4, 4) AS INTEGER) <= 2024 
                                AND (p."T1" > 0 OR p."N1" > 0 OR p."C1" > 0) 
                            THEN p."N° d'ordre" 
                        END) as nb_aides_cumul_2024,
                        SUM(CASE 
                            WHEN CAST(SUBSTRING(p."Date OV", -4, 4) AS INTEGER) <= 2024 
                            THEN COALESCE(p."T1", 0) + COALESCE(p."N1", 0) + COALESCE(p."C1", 0) + 
                                 COALESCE(p."T2", 0) + COALESCE(p."N2", 0) + COALESCE(p."C2", 0) +
                                 COALESCE(p."T3", 0)
                            ELSE 0 
                        END) as montant_cumul_2024,
                        COUNT(DISTINCT CASE 
                            WHEN CAST(SUBSTRING(p."Date OV", -4, 4) AS INTEGER) = 2025 
                                AND CAST(SUBSTRING(p."Date OV", POSITION('/' IN p."Date OV") + 1, 2) AS INTEGER) <= {month_number}
                                AND (p."T1" > 0 OR p."N1" > 0 OR p."C1" > 0) 
                            THEN p."N° d'ordre" 
                        END) as nb_aides_2025,
                        SUM(CASE 
                            WHEN CAST(SUBSTRING(p."Date OV", -4, 4) AS INTEGER) = 2025 
                                AND CAST(SUBSTRING(p."Date OV", POSITION('/' IN p."Date OV") + 1, 2) AS INTEGER) <= {month_number}
                            THEN COALESCE(p."T1", 0) + COALESCE(p."N1", 0) + COALESCE(p."C1", 0) + 
                                 COALESCE(p."T2", 0) + COALESCE(p."N2", 0) + COALESCE(p."C2", 0) +
                                 COALESCE(p."T3", 0)
                            ELSE 0 
                        END) as montant_2025
                    FROM decisions d
                    LEFT JOIN paiements p ON d."Code déc" = p."Code T3"
                    WHERE d."Sous programme" LIKE '%{year}%'
                    GROUP BY daira, commune
                    ORDER BY daira, commune
                """,
        # Totaux généraux
        "totals": """
                    SELECT 
                        COUNT(DISTINCT d."Code déc") as total_aides_inscrits,
                        COUNT(DISTINCT CASE WHEN p."N° d'ordre" IS NOT NULL THEN d."Code déc" END) as total_aides_bnh,
                        SUM(CASE WHEN p."N° d'ordre" IS NOT NULL THEN COALESCE(d."Financier", 0) ELSE 0 END) as total_montants_inscrits,
                        COUNT(DISTINCT CASE WHEN p."T1" > 0 OR p."N1" > 0 OR p."C1" > 0 THEN p."N° d'ordre" END) as total_aides_lances,
                        SUM(CASE WHEN p."T1" > 0 OR p."N1" > 0 OR p."C1" > 0 THEN COALESCE(p."T1", 0) + COALESCE(p."N1", 0) + COALESCE(p."C1", 0) ELSE 0 END) as total_montants_decrits,
                        COUNT(DISTINCT CASE WHEN d."Type" = 'Décision' THEN d."Code déc" END) as total_aides_mdv,
                        SUM(CASE WHEN d."Type" = 'Décision' THEN COALESCE(d."Financier", 0) ELSE 0 END) as total_montants_mdv,
                        COUNT(DISTINCT CASE 
                            WHEN CAST(SUBSTRING(p."Date OV", -4, 4) AS INTEGER) <= 2024 
                                AND (p."T1" > 0 OR p."N1" > 0 OR p."C1" > 0) 
                            THEN p."N° d'ordre" 
                        END) as total_aides_cumul_2024,
                        SUM(CASE 
                            WHEN CAST(SUBSTRING(p."Date OV", -4, 4) AS INTEGER) <= 2024 
                            THEN COALESCE(p."T1", 0) + COALESCE(p."N1", 0) + COALESCE(p."C1", 0) + 
                                 COALESCE(p."T2", 0) + COALESCE(p."N2", 0) + COALESCE(p."C2", 0) +
                                 COALESCE(p."T3", 0)
                            ELSE 0 
                        END) as total_montant_cumul_2024,
                        COUNT(DISTINCT CASE 
                            WHEN CAST(SUBSTRING(p."Date OV", -4, 4) AS INTEGER) = 2025 
                                AND CAST(SUBSTRING(p."Date OV", POSITION('/' IN p."Date OV") + 1, 2) AS INTEGER) <= {month_number}
                                AND (p."T1" > 0 OR p."N1" > 0 OR p."C1" > 0) 
                            THEN p."N° d'ordre" 
                        END) as total_aides_2025,
                        SUM(CASE 
                            WHEN CAST(SUBSTRING(p."Date OV", -4, 4) AS INTEGER) = 2025 
                                AND CAST(SUBSTRING(p."Date OV", POSITION('/' IN p."Date OV") + 1, 2) AS INTEGER) <= {month_number}
                            THEN COALESCE(p."T1", 0) + COALESCE(p."N1", 0) + COALESCE(p."C1", 0) + 
                                 COALESCE(p."T2", 0) + COALESCE(p."N2", 0) + COALESCE(p."C2", 0) +
                                 COALESCE(p."T3", 0)
                            ELSE 0 
                        END) as total_montant_2025
                    FROM decisions d
                    LEFT JOIN paiements p ON d."Code déc" = p."Code T3"
                    WHERE d."Sous programme" LIKE '%{year}%'
                """,
    },
    output_filename="Situation_financière_des_programmes_{wilaya}_{date}.xlsx",
    generator=SituationFinanciereGenerator,
)
