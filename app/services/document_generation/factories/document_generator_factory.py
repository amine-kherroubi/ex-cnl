from __future__ import annotations

"""
Fabrique pour la création de générateurs de documents.

Ce module implémente le pattern Factory pour créer des instances
de générateurs de documents selon le type demandé. Il maintient
un registre des générateurs disponibles et orchestre leur
initialisation avec les dépendances appropriées.

La fabrique découple la logique de création des générateurs
de leur utilisation, facilitant l'ajout de nouveaux types
de documents.
"""

# Imports de la bibliothèque standard
from logging import Logger

# Imports de l'application locale
from app.data.data_repository import DataRepository
from app.services.document_generation.concrete_generators.activite_mensuelle_hr import (
    ActiviteMensuelleHRGenerator,
)
from app.services.document_generation.models.document_context import (
    DocumentContext,
)
from app.services.document_generation.document_registry import (
    DocumentRegistry,
    DocumentSpecification,
)
from app.services.document_generation.document_generator_template import (
    DocumentGenerator,
)
from app.services.io.io_service import IOService
from app.utils.logging_setup import get_logger


class DocumentGeneratorFactory:
    """
    Fabrique pour la création de générateurs de documents.

    Cette classe implémente le pattern Factory pour créer des instances
    de générateurs de documents. Elle maintient un registre des générateurs
    disponibles et gère leur initialisation avec les bonnes dépendances.

    La fabrique permet l'ajout facile de nouveaux types de générateurs
    sans modification du code client.

    Attributs:
        _generators: Dictionnaire mappant les noms de documents aux classes génératrices

    Exemples:
        >>> generator = DocumentGeneratorFactory.create_generator(
        ...     document_name="activite_mensuelle_par_programme",
        ...     storage_service=storage_service,
        ...     data_repository=data_repository,
        ...     document_context=context
        ... )
        >>> generator.generate()  # Génère le document
    """

    _logger: Logger = get_logger("app.services.generator_factory")

    # Registre des générateurs disponibles
    # Mapping : nom du document -> classe du générateur
    _generators: dict[str, type[DocumentGenerator]] = {
        "activite_mensuelle_par_programme": ActiviteMensuelleHRGenerator,
    }

    @classmethod
    def create_generator(
        cls,
        document_name: str,
        storage_service: IOService,
        data_repository: DataRepository,
        document_context: DocumentContext,
    ) -> DocumentGenerator:
        """
        Crée un générateur de document selon le nom spécifié.

        Cette méthode orchestre la création d'un générateur en :
        1. Validant l'existence du générateur demandé
        2. Récupérant la spécification du document
        3. Instanciant le générateur avec ses dépendances

        Args:
            document_name: Nom unique du document à générer
            storage_service: Service de gestion des fichiers d'entrée/sortie
            data_repository: Dépôt de données pour l'exécution de requêtes SQL
            document_context: Contexte contenant les paramètres de génération

        Returns:
            Instance du générateur configuré et prêt à utiliser

        Raises:
            ValueError: Si le document demandé n'existe pas dans le registre
            Exception: Si la création du générateur échoue pour une autre raison
        """
        cls._logger.info(f"Création du générateur pour le document : {document_name}")
        cls._logger.debug(f"Générateurs disponibles : {list(cls._generators.keys())}")

        # Validation de l'existence du générateur
        if document_name not in cls._generators:
            error_msg: str = f"Document inconnu : {document_name}"
            cls._logger.error(
                f"{error_msg}. Disponibles : {list(cls._generators.keys())}"
            )
            raise ValueError(error_msg)

        try:
            # Récupération de la spécification du document
            document_specification: DocumentSpecification = DocumentRegistry.get(
                document_name
            )
            cls._logger.debug(
                f"Spécification du document récupérée : {document_specification.display_name}"
            )

            # Récupération de la classe génératrice
            generator_class: type[DocumentGenerator] = cls._generators[document_name]
            cls._logger.debug(
                f"Utilisation de la classe génératrice : {generator_class.__name__}"
            )

            # Création de l'instance du générateur
            generator: DocumentGenerator = generator_class(
                storage_service,
                data_repository,
                document_specification,
                document_context,
            )

            cls._logger.info(
                f"{generator_class.__name__} créé avec succès pour le document '{document_name}'"
            )
            cls._logger.debug(
                f"Contexte du générateur : wilaya={document_context.wilaya.value}, date={document_context.report_date}"
            )

            return generator

        except Exception as error:
            cls._logger.error(
                f"Échec de la création du générateur pour le document '{document_name}' : {error}"
            )
            raise
