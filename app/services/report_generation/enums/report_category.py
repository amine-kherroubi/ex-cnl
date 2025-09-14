from __future__ import annotations

"""
Énumération des catégories de reports.

Ce module définit les différentes catégories thématiques
des reports administratifs supportés par le système.

Les catégories permettent de classifier et organiser
les reports selon leur domaine d'application.
"""

# Imports de la bibliothèque standard
from enum import StrEnum


class ReportCategory(StrEnum):
    """
    Énumération des catégories de reports administratifs.

    Cette énumération classe les reports selon leur domaine
    d'intervention administratif. Actuellement, seule la catégorie
    "Habitat rural" est définie, mais d'autres catégories peuvent
    être ajoutées selon les besoins (habitat urbain, infrastructures, etc.).

    Exemples:
        >>> category = ReportCategory.HABITAT_RURAL
        >>> print(category.value)  # "Habitat rural"
    """

    HABITAT_RURAL = "Habitat rural"
