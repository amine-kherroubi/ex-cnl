from __future__ import annotations

"""
Modèle de spécification pour les reports générés.

Ce module définit la structure complète d'une spécification de report,
incluant les métadonnées, les requêtes SQL, les fichiers requis et
la classe génératrice associée.

La spécification sert de blueprint pour la génération de reports
et centralise toutes les informations nécessaires au processus.
"""

# Imports de la bibliothèque standard
from typing import Annotated

# Imports tiers
from pydantic import BaseModel, Field

# Imports de l'application locale
from app.services.report_generation.report_generator_template import (
    ReportGenerator,
)
from app.services.report_generation.enums.report_category import ReportCategory
from app.services.report_generation.enums.space_time import Periodicity


class ReportSpecification(BaseModel):
    """
    Spécification complète d'un report administratif.

    Cette classe définit tous les paramètres nécessaires à la génération
    d'un report : métadonnées descriptives, fichiers d'entrée requis,
    requêtes de données, format de sortie et classe génératrice.

    Attributes:
        name: Nom interne unique du report
        display_name: Nom d'affichage pour l'utilisateur
        category: Catégorie du report (ex: Habitat Rural)
        periodicity: Fréquence de génération (mensuel, semestriel, annuel)
        description: Description détaillée du but du report
        required_files: Mapping des patterns de fichiers vers les noms de vues
        queries: Mapping des noms de requêtes vers les requêtes SQL
        output_filename: Template du nom de fichier de sortie
        generator: Classe génératrice concrète pour ce report

    Exemple:
        >>> spec = ReportSpecification(
        ...     name="activite_mensuelle",
        ...     display_name="Activité mensuelle",
        ...     category=ReportCategory.HABITAT_RURAL,
        ...     periodicity=Periodicity.MONTHLY,
        ...     description="Rapport mensuel d'activité par programme",
        ...     required_files={"pattern.*\\.xlsx": "vue_donnees"},
        ...     queries={"total": "SELECT COUNT(*) FROM vue_donnees"},
        ...     output_filename="rapport_{date}.xlsx",
        ...     generator=MonGenerateur
        ... )
    """

    name: Annotated[
        str,
        Field(
            description="Nom interne unique du report",
            min_length=1,
        ),
    ]

    display_name: Annotated[
        str,
        Field(
            description="Nom lisible du report pour l'affichage utilisateur",
            min_length=1,
        ),
    ]

    category: Annotated[
        ReportCategory,
        Field(description="Catégorie thématique du report"),
    ]

    periodicity: Annotated[
        Periodicity, Field(description="Fréquence de génération du report")
    ]

    description: Annotated[
        str,
        Field(description="Description détaillée de l'objectif du report"),
    ]

    required_files: Annotated[
        dict[str, str],
        Field(
            description="Mapping des patterns regex de noms de fichiers vers les noms de vues SQL correspondantes"
        ),
    ]

    queries: Annotated[
        dict[str, str],
        Field(
            description="Mapping des noms de requêtes vers les templates SQL correspondants"
        ),
    ]

    output_filename: Annotated[
        str,
        Field(description="Template du nom de fichier Excel à générer en sortie"),
    ]

    generator: Annotated[
        type[ReportGenerator],
        Field(
            description="Classe génératrice concrète responsable de la production du report"
        ),
    ]

    model_config = {
        "frozen": True,  # Immutabilité après création
        "str_strip_whitespace": True,  # Suppression automatique des espaces
        "validate_assignment": True,  # Validation lors des assignations
    }
