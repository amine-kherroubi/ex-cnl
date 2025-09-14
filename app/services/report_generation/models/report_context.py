from __future__ import annotations

"""
Modèle de contexte pour la génération de reports.

Ce module définit la structure des données contextuelles nécessaires
à la génération de reports administratifs. Le contexte contient
les informations temporelles et géographiques qui paramètrent
la génération des rapports.

Le modèle utilise Pydantic pour la validation automatique des données
et garantit la cohérence des informations fournies.
"""

# Imports de la bibliothèque standard
from datetime import date

# Imports tiers
from pydantic import BaseModel, Field, field_validator

# Imports de l'application locale
from app.services.report_generation.enums.space_time import Wilaya, Month


class ReportContext(BaseModel):
    """
    Contexte de génération d'un report administratif.

    Cette classe encapsule toutes les informations contextuelles
    nécessaires à la génération d'un report : localisation
    géographique, période temporelle et date de référence.

    Attributes:
        wilaya: Division administrative algérienne concernée
        year: Année de la période de rapport
        report_date: Date spécifique de génération ou d'extraction des données
        month: Mois pour les rapports mensuels (optionnel)
        semester: Semestre pour les rapports semestriels (optionnel)

    Exemples:
        Contexte mensuel :
        >>> context = ReportContext(
        ...     wilaya=Wilaya.ALGER,
        ...     year=2024,
        ...     month=Month.JANVIER,
        ...     report_date=date(2024, 1, 31)
        ... )

        Contexte annuel :
        >>> context = ReportContext(
        ...     wilaya=Wilaya.CONSTANTINE,
        ...     year=2023,
        ...     report_date=date(2023, 12, 31)
        ... )
    """

    wilaya: Wilaya = Field(
        description="Division administrative algérienne pour ce report",
    )

    year: int = Field(
        description="Année de la période de rapport",
        ge=2000,  # Année minimale acceptable
        le=2100,  # Année maximale acceptable
    )

    report_date: date = Field(
        description="Date spécifique de génération du rapport ou d'extraction des données",
    )

    # Champs optionnels - utilisés uniquement selon le contexte
    month: Month | None = Field(
        default=None,
        description="Mois de la période de rapport en français (pour rapports mensuels)",
    )

    semester: int | None = Field(
        default=None,
        description="Semestre (1 ou 2) pour les rapports semestriels",
        ge=1,  # Premier semestre
        le=2,  # Second semestre
    )

    @field_validator("report_date")
    @classmethod
    def validate_report_date(cls, report_date: date) -> date:
        """
        Valide que la date de rapport n'est pas dans le futur.

        Args:
            report_date: Date à valider

        Returns:
            Date validée

        Raises:
            ValueError: Si la date est postérieure à aujourd'hui
        """
        if report_date > date.today():
            raise ValueError("La date de rapport ne peut pas être dans le futur")
        return report_date

    model_config = {
        "frozen": True,  # Immutabilité après création
        "str_strip_whitespace": True,  # Suppression automatique des espaces
        "validate_assignment": True,  # Validation lors des assignations
    }
