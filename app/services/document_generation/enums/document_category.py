from __future__ import annotations

"""
Énumération des catégories de documents.

Ce module définit les différentes catégories thématiques
des documents administratifs supportés par le système.

Les catégories permettent de classifier et organiser
les documents selon leur domaine d'application.
"""

# Imports de la bibliothèque standard
from enum import StrEnum


class DocumentCategory(StrEnum):
    """
    Énumération des catégories de documents administratifs.

    Cette énumération classe les documents selon leur domaine
    d'intervention administratif. Actuellement, seule la catégorie
    "Habitat rural" est définie, mais d'autres catégories peuvent
    être ajoutées selon les besoins (habitat urbain, infrastructures, etc.).

    Exemples:
        >>> category = DocumentCategory.HABITAT_RURAL
        >>> print(category.value)  # "Habitat rural"
    """

    HABITAT_RURAL = "Habitat rural"
