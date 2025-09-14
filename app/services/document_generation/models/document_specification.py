from __future__ import annotations

"""
Modèle de spécification pour les documents générés.

Ce module définit la structure complète d'une spécification de document,
incluant les métadonnées, les requêtes SQL, les fichiers requis et
la classe génératrice associée.

La spécification sert de blueprint pour la génération de documents
et centralise toutes les informations nécessaires au processus.
"""

# Imports de la bibliothèque standard
from typing import Annotated

# Imports tiers
from pydantic import BaseModel, Field

# Imports de l'application locale
from app.services.document_generation.document_generator_template import (
    DocumentGenerator,
)
from app.services.document_generation.enums.document_category import DocumentCategory
from app.services.document_generation.enums.space_time import Periodicity


class DocumentSpecification(BaseModel):
    """
    Spécification complète d'un document administratif.

    Cette classe définit tous les paramètres nécessaires à la génération
    d'un document : métadonnées descriptives, fichiers d'entrée requis,
    requêtes de données, format de sortie et classe génératrice.

    Attributes:
        name: Nom interne unique du document
        display_name: Nom d'affichage pour l'utilisateur
        category: Catégorie du document (ex: Habitat Rural)
        periodicity: Fréquence de génération (mensuel, semestriel, annuel)
        description: Description détaillée du but du document
        required_files: Mapping des patterns de fichiers vers les noms de vues
        queries: Mapping des noms de requêtes vers les requêtes SQL
        output_filename: Template du nom de fichier de sortie
        generator: Classe génératrice concrète pour ce document

    Exemple:
        >>> spec = DocumentSpecification(
        ...     name="activite_mensuelle",
        ...     display_name="Activité mensuelle",
        ...     category=DocumentCategory.HABITAT_RURAL,
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
            description="Nom interne unique du document",
            min_length=1,
        ),
    ]

    display_name: Annotated[
        str,
        Field(
            description="Nom lisible du document pour l'affichage utilisateur",
            min_length=1,
        ),
    ]

    category: Annotated[
        DocumentCategory,
        Field(description="Catégorie thématique du document"),
    ]

    periodicity: Annotated[
        Periodicity, Field(description="Fréquence de génération du document")
    ]

    description: Annotated[
        str,
        Field(description="Description détaillée de l'objectif du document"),
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
        type[DocumentGenerator],
        Field(
            description="Classe génératrice concrète responsable de la production du document"
        ),
    ]

    model_config = {
        "frozen": True,  # Immutabilité après création
        "str_strip_whitespace": True,  # Suppression automatique des espaces
        "validate_assignment": True,  # Validation lors des assignations
    }
