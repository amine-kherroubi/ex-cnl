from __future__ import annotations

"""
Registre centralisé des spécifications de reports.

Ce module implémente le pattern Registry pour maintenir un catalogue
de toutes les spécifications de reports supportées par l'application.
Il fournit un point d'accès unique pour récupérer les définitions
de reports avec leurs requêtes, générateurs et métadonnées.

Le registre centralise la configuration des reports et facilite
l'ajout de nouveaux types de reports.
"""

# Imports de la bibliothèque standard
from typing import Final, final

# Imports de l'application locale
from app.services.report_generation.concrete_generators.activite_mensuelle_hr import (
    ActiviteMensuelleHRGenerator,
)
from app.services.report_generation.models.report_specification import (
    ReportCategory,
    ReportSpecification,
)
from app.services.report_generation.enums.space_time import Periodicity


@final
class RerportSpecificationRegistry(object):
    """
    Registre centralisé des spécifications de reports disponibles.

    Cette classe implémente le pattern Registry pour maintenir un catalogue
    de toutes les spécifications de reports supportées par l'application.
    Elle fournit un point d'accès unique pour récupérer les définitions
    de reports avec leurs requêtes, générateurs et métadonnées.

    Le décorateur @final empêche l'héritage et __slots__ vide optimise
    l'utilisation mémoire. Cette classe n'est pas destinée à être
    instanciée (pattern Registry statique).

    Exemples:
        Récupération d'une spécification :
        >>> spec = ReportRegistry.get("activite_mensuelle_par_programme")
        >>> print(spec.display_name)  # "Activité mensuelle"

        Vérification d'existence :
        >>> if ReportRegistry.has("mon_report"):
        ...     spec = ReportRegistry.get("mon_report")

        Liste de tous les reports :
        >>> all_docs = ReportRegistry.all()
        >>> print(list(all_docs.keys()))
    """

    __slots__ = ()

    def __init__(self):
        """
        Constructeur privé - cette classe n'est pas destinée à être instanciée.

        Le registre fonctionne uniquement avec des méthodes de classe
        statiques pour maintenir un état global cohérent.

        Raises:
            TypeError: Toujours levée car cette classe est un registre statique
        """
        raise TypeError(
            f"{self.__class__.__name__} n'est pas destinée à être instanciée"
        )

    @classmethod
    def get(cls, report_name: str) -> ReportSpecification:
        """
        Récupère la spécification d'un report par son nom.

        Args:
            report_name: Nom unique du report à récupérer

        Returns:
            Spécification complète du report demandé

        Raises:
            ValueError: Si le report n'existe pas dans le registre
        """
        if report_name not in cls._REPORT_SPECIFICATIONS:
            available = list(cls._REPORT_SPECIFICATIONS.keys())
            raise ValueError(
                f"Report '{report_name}' introuvable. Disponibles : {available}"
            )
        return cls._REPORT_SPECIFICATIONS[report_name]

    @classmethod
    def has(cls, report_name: str) -> bool:
        """
        Vérifie si un report existe dans le registre.

        Args:
            report_name: Nom du report à vérifier

        Returns:
            True si le report existe, False sinon
        """
        return report_name in cls._REPORT_SPECIFICATIONS

    @classmethod
    def all(cls) -> dict[str, ReportSpecification]:
        """
        Retourne toutes les spécifications de reports disponibles.

        Returns:
            Dictionnaire contenant toutes les spécifications de reports,
            avec les noms comme clés et les spécifications comme valeurs.
            Retourne une copie pour préserver l'immutabilité du registre.
        """
        return cls._REPORT_SPECIFICATIONS.copy()

    # Définitions statiques de tous les reports supportés
    _REPORT_SPECIFICATIONS: Final[dict[str, ReportSpecification]] = {
        "activite_mensuelle_par_programme": ReportSpecification(
            name="activite_mensuelle_par_programme",
            display_name="Activité mensuelle",
            category=ReportCategory.HABITAT_RURAL,
            periodicity=Periodicity.MONTHLY,
            description=(
                "Report de suivi mensuel des activités par programme, "
                "renseigné par la BNH (ex-CNL). Comprend les lancements et livraisons "
                "ainsi que la situation globale des programmes."
            ),
            # Fichiers requis avec patterns regex pour validation
            # Le pattern correspond aux journaux de paiements générés par le système
            required_files={
                r"^Journal_paiements__Agence_[A-Z+]+_\d{2}\.\d{2}\.\d{4}_[0-9]+.xlsx$": "paiements",
            },
            # Ensemble de requêtes SQL pour extraire les données nécessaires
            queries={
                # --- REQUÊTES POUR LE PREMIER TABLEAU (ACTIVITÉ MENSUELLE) ---
                # Liste des programmes triés par ordre d'affichage
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
                # --- REQUÊTES POUR LE SECOND TABLEAU (SITUATION DES PROGRAMMES) ---
                # Programmes avec leur consistance (nombre de logements planifiés)
                "programmes_situation": """
                    SELECT 
                        programme,
                        consistance,
                        display_order
                    FROM programmes
                    ORDER BY display_order
                """,
                # Logements achevés - ayant reçu la dernière tranche de paiement
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
                # Calcul des logements en cours (lancés mais non achevés)
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
                # Logements non encore lancés (consistance - premières tranches payées)
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
            # Template du nom de fichier de sortie avec variables dynamiques
            output_filename="Activité_mensuelle_par_programme_{wilaya}_{date}.xlsx",
            # Classe responsable de la génération du report
            generator=ActiviteMensuelleHRGenerator,
        ),
    }
