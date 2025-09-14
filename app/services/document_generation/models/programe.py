from __future__ import annotations

"""
Modèle de programme d'habitat rural.

Ce module définit la structure d'un programme de logements ruraux,
avec ses métadonnées temporelles et quantitatives. Les programmes
constituent l'unité organisationnelle de base pour le suivi des
projets de logements.

Chaque programme correspond à une initiative gouvernementale
spécifique avec des objectifs de construction définis.
"""

# Imports de la bibliothèque standard
from typing import Annotated

# Imports tiers
from pydantic import BaseModel, Field


class Programme(BaseModel):
    """
    Représentation d'un programme de logements ruraux.

    Un programme définit une initiative gouvernementale de construction
    de logements avec une période d'exécution et des objectifs quantitatifs.
    Il sert d'unité de regroupement pour le suivi et le reporting.

    Attributes:
        name: Nom officiel du programme
        year_start: Année de début du programme
        year_end: Année de fin du programme (None si en cours)
        display_order: Ordre d'affichage dans les rapports
        consistance: Nombre total de logements planifiés

    Exemples:
        Programme quinquennal :
        >>> programme = Programme(
        ...     name="QUINQU 2020-2024",
        ...     year_start=2020,
        ...     year_end=2024,
        ...     display_order=1,
        ...     consistance=40000
        ... )

        Programme en cours :
        >>> programme_actuel = Programme(
        ...     name="PROGRAMME 2025",
        ...     year_start=2025,
        ...     year_end=None,  # Programme encore en cours
        ...     display_order=2,
        ...     consistance=5000
        ... )
    """

    name: Annotated[
        str,
        Field(
            description="Nom officiel du programme de logements",
            min_length=1,
        ),
    ]

    year_start: Annotated[
        int,
        Field(description="Année de démarrage du programme"),
    ]

    year_end: Annotated[
        int | None,
        Field(
            default=None,
            description="Année de fin du programme, None si le programme est en cours",
        ),
    ]

    display_order: Annotated[
        int,
        Field(
            default=0,
            description="Ordre d'affichage du programme dans les rapports et tableaux",
        ),
    ]

    consistance: Annotated[
        int,
        Field(
            default=0,
            description="Nombre total de logements planifiés dans ce programme",
            ge=0,  # Ne peut pas être négatif
        ),
    ]

    model_config = {
        "frozen": True,  # Immutabilité après création
        "str_strip_whitespace": True,  # Suppression automatique des espaces
        "validate_assignment": True,  # Validation lors des assignations
    }
