from __future__ import annotations

# Imports de la bibliothèque standard
from typing import Final, final

# Imports de l'application locale
from app.services.document_generation.concrete_generators.activite_mensuelle_hr import (
    ActiviteMensuelleHRGenerator,
)
from app.services.document_generation.models.document_specification import (
    DocumentCategory,
    DocumentSpecification,
)
from app.services.document_generation.enums.space_time import Periodicity


@final
class DocumentRegistry(object):
    """
    Registre centralisé des spécifications de documents disponibles.

    Cette classe implémente le pattern Registry pour maintenir un catalogue
    de toutes les spécifications de documents supportées par l'application.
    Elle fournit un point d'accès unique pour récupérer les définitions
    de documents avec leurs requêtes, générateurs et métadonnées.

    Utilise le décorateur @final pour empêcher l'héritage et __slots__ vide
    pour optimiser l'utilisation mémoire. Cette classe n'est pas destinée
    à être instanciée (pattern Registry statique).
    """

    __slots__ = ()

    def __init__(self):
        """
        Constructeur privé - cette classe n'est pas destinée à être instanciée.

        Raises:
            TypeError: Toujours levée car cette classe est un registre statique
        """
        raise TypeError(
            f"{self.__class__.__name__} n'est pas destinée à être instanciée"
        )

    @classmethod
    def get(cls, document_name: str) -> DocumentSpecification:
        """
        Récupère la spécification d'un document par son nom.

        Args:
            document_name: Nom unique du document à récupérer

        Returns:
            Spécification complète du document demandé

        Raises:
            ValueError: Si le document n'existe pas dans le registre
        """
        if document_name not in cls._DOCUMENTS_DEFINITIONS:
            available = list(cls._DOCUMENTS_DEFINITIONS.keys())
            raise ValueError(
                f"Document '{document_name}' introuvable. Disponibles : {available}"
            )
        return cls._DOCUMENTS_DEFINITIONS[document_name]

    @classmethod
    def has(cls, document_name: str) -> bool:
        """
        Vérifie si un document existe dans le registre.

        Args:
            document_name: Nom du document à vérifier

        Returns:
            True si le document existe, False sinon
        """
        return document_name in cls._DOCUMENTS_DEFINITIONS

    @classmethod
    def all(cls) -> dict[str, DocumentSpecification]:
        """
        Retourne toutes les spécifications de documents disponibles.

        Returns:
            Dictionnaire contenant toutes les spécifications de documents,
            avec les noms comme clés et les spécifications comme valeurs.
            Retourne une copie pour préserver l'immutabilité du registre.
        """
        return cls._DOCUMENTS_DEFINITIONS.copy()

    # Définitions statiques de tous les documents supportés
    _DOCUMENTS_DEFINITIONS: Final[dict[str, DocumentSpecification]] = {
        "activite_mensuelle_par_programme": DocumentSpecification(
            name="activite_mensuelle_par_programme",
            display_name="Activité mensuelle",
            category=DocumentCategory.HABITAT_RURAL,
            periodicity=Periodicity.MONTHLY,
            description=(
                "Document de suivi mensuel des activités par programme, "
                "renseigné par la BNH (ex-CNL)"
            ),
            # Fichiers requis avec patterns regex pour validation
            required_files={
                r"^Journal_paiements__Agence_[A-Z+]+_\d{2}\.\d{2}\.\d{4}_[0-9]+.xlsx$": "paiements",
            },
            # Ensemble de requêtes SQL pour extraire les données nécessaires
            queries={
                # Requêtes pour le premier tableau (ACTIVITÉ MENSUELLE)
                "programmes": """
                    SELECT programme
                    FROM programmes
                    ORDER BY display_order
                    """,
                # Lancements du mois - première tranche de paiement
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
                # Livraisons du mois - dernière tranche de paiement
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
                # Requêtes pour le second tableau (SITUATION DES PROGRAMMES)
                "programmes_situation": """
                    SELECT 
                        programme,
                        consistance,
                        display_order
                    FROM programmes
                    ORDER BY display_order
                    """,
                # Logements achevés - ayant reçu la dernière tranche
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
                # Calcul des logements en cours par différence (méthode plus fiable)
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
                # Logements non encore lancés - n'ayant pas reçu la première tranche
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
            # Classe responsable de la génération du document
            generator=ActiviteMensuelleHRGenerator,
        ),
    }
