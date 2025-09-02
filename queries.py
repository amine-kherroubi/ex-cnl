from __future__ import annotations


def get_queries() -> dict[str, str]:
    return {
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
        "first_tranche_count": """
            SELECT c.Commune,
                   COALESCE((SELECT COUNT(*)
                    FROM ovs o
                    WHERE (NOTIFICATION = 'N°: 1132. Du: 16/07/2013. TRANCHE: 2. Montant:    700 000' OR
                           NOTIFICATION = 'N°:1132.Du:16/07/2013.TRANCHE:2.Montant:   700 000') 
                      AND "Sous programme" = 'PQ2013'
                      AND "Annulé?" = 'non'
                      AND Tranche IN ('60%  1+2 EME TRANCHE',
                                      '20%  1 ERE TRANCHE',
                                      '100%  Tranche totale',
                                      '60%  Première Tranche',
                                      '100%  1+2+3 EME TRANCHE',
                                      '40%  Première Tranche')
                      AND o.Commune = c.Commune
                   ), 0) AS tranche_count
            FROM commune c
            ORDER BY c.Commune
        """,
    }
