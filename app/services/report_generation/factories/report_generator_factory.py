from __future__ import annotations

"""
Fabrique pour la création de générateurs de reports.

Ce module implémente le pattern Factory pour créer des instances
de générateurs de reports selon le type demandé. Il maintient
un registre des générateurs disponibles et orchestre leur
initialisation avec les dépendances appropriées.

La fabrique découple la logique de création des générateurs
de leur utilisation, facilitant l'ajout de nouveaux types
de reports.
"""

# Imports de la bibliothèque standard
from logging import Logger

# Imports de l'application locale
from app.data.data_repository import DataRepository
from app.services.report_generation.concrete_generators.activite_mensuelle_hr import (
    ActiviteMensuelleHRGenerator,
)
from app.services.report_generation.models.report_context import (
    ReportContext,
)
from app.services.report_generation.report_specification_registry import (
    RerportSpecificationRegistry,
    ReportSpecification,
)
from app.services.report_generation.report_generator_template import (
    ReportGenerator,
)
from app.services.file_io.file_io_service import FileIOService
from app.utils.logging_setup import get_logger


class ReportGeneratorFactory:
    """
    Fabrique pour la création de générateurs de reports.

    Cette classe implémente le pattern Factory pour créer des instances
    de générateurs de reports. Elle maintient un registre des générateurs
    disponibles et gère leur initialisation avec les bonnes dépendances.

    La fabrique permet l'ajout facile de nouveaux types de générateurs
    sans modification du code client.

    Attributs:
        _generators: Dictionnaire mappant les noms de reports aux classes génératrices

    Exemples:
        >>> generator = ReportGeneratorFactory.create_generator(
        ...     report_name="activite_mensuelle_par_programme",
        ...     storage_service=storage_service,
        ...     data_repository=data_repository,
        ...     report_context=context
        ... )
        >>> generator.generate()  # Génère le report
    """

    _logger: Logger = get_logger("app.services.generator_factory")

    # Registre des générateurs disponibles
    # Mapping : nom du report -> classe du générateur
    _generators: dict[str, type[ReportGenerator]] = {
        "activite_mensuelle_par_programme": ActiviteMensuelleHRGenerator,
    }

    @classmethod
    def create_generator(
        cls,
        report_name: str,
        storage_service: FileIOService,
        data_repository: DataRepository,
        report_context: ReportContext,
    ) -> ReportGenerator:
        """
        Crée un générateur de report selon le nom spécifié.

        Cette méthode orchestre la création d'un générateur en :
        1. Validant l'existence du générateur demandé
        2. Récupérant la spécification du report
        3. Instanciant le générateur avec ses dépendances

        Args:
            report_name: Nom unique du report à générer
            storage_service: Service de gestion des fichiers d'entrée/sortie
            data_repository: Dépôt de données pour l'exécution de requêtes SQL
            report_context: Contexte contenant les paramètres de génération

        Returns:
            Instance du générateur configuré et prêt à utiliser

        Raises:
            ValueError: Si le report demandé n'existe pas dans le registre
            Exception: Si la création du générateur échoue pour une autre raison
        """
        cls._logger.info(f"Création du générateur pour le report : {report_name}")
        cls._logger.debug(f"Générateurs disponibles : {list(cls._generators.keys())}")

        # Validation de l'existence du générateur
        if report_name not in cls._generators:
            error_msg: str = f"Report inconnu : {report_name}"
            cls._logger.error(
                f"{error_msg}. Disponibles : {list(cls._generators.keys())}"
            )
            raise ValueError(error_msg)

        try:
            # Récupération de la spécification du report
            report_specification: ReportSpecification = (
                RerportSpecificationRegistry.get(report_name)
            )
            cls._logger.debug(
                f"Spécification du report récupérée : {report_specification.display_name}"
            )

            # Récupération de la classe génératrice
            generator_class: type[ReportGenerator] = cls._generators[report_name]
            cls._logger.debug(
                f"Utilisation de la classe génératrice : {generator_class.__name__}"
            )

            # Création de l'instance du générateur
            generator: ReportGenerator = generator_class(
                storage_service,
                data_repository,
                report_specification,
                report_context,
            )

            cls._logger.info(
                f"{generator_class.__name__} créé avec succès pour le report '{report_name}'"
            )
            cls._logger.debug(
                f"Contexte du générateur : wilaya={report_context.wilaya.value}, date={report_context.report_date}"
            )

            return generator

        except Exception as error:
            cls._logger.error(
                f"Échec de la création du générateur pour le report '{report_name}' : {error}"
            )
            raise
