from __future__ import annotations

# Imports de la bibliothèque standard
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable
from logging import Logger

# Imports tiers
import pandas as pd
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

# Imports de l'application locale
from app.data.data_repository import DataRepository
from app.services.document_generation.business_values.programmes import (
    get_programmes_dataframe,
)
from app.services.file_io.file_io_service import FileIOService
from app.services.document_generation.models.document_context import (
    DocumentContext,
)
from app.utils.exceptions import QueryExecutionError
from app.utils.date_formatting import DateFormatter
from app.utils.logging_setup import get_logger

if TYPE_CHECKING:
    from app.services.document_generation.document_registry import (
        DocumentSpecification,
    )


class DocumentGenerator(ABC):
    """
    Classe abstraite de base pour la génération de documents.

    Cette classe implémente le pattern Template Method pour définir l'algorithme
    de génération de documents en plusieurs étapes bien définies. Les sous-classes
    sont responsables de l'implémentation des détails spécifiques à chaque type
    de document (en-tête, tableaux, pied de page, formatage).

    Le processus de génération suit ces étapes :
    1. Validation des fichiers requis
    2. Chargement des données en base
    3. Création des tables de référence
    4. Exécution des requêtes de données
    5. Création du classeur Excel
    6. Ajout de l'en-tête (responsabilité des sous-classes)
    7. Construction des tableaux (responsabilité des sous-classes)
    8. Ajout du pied de page (responsabilité des sous-classes)
    9. Formatage final (responsabilité des sous-classes)
    10. Sauvegarde du document

    Utilise __slots__ pour optimiser l'utilisation mémoire.
    """

    __slots__ = (
        "_storage_service",
        "_data_repository",
        "_document_specification",
        "_document_context",
        "_workbook",
        "_logger",
    )

    def __init__(
        self,
        storage_service: FileIOService,
        data_repository: DataRepository,
        document_specification: DocumentSpecification,
        document_context: DocumentContext,
    ) -> None:
        """
        Initialise le générateur de documents avec les services et contextes nécessaires.

        Args:
            storage_service: Service de gestion des fichiers d'entrée/sortie
            data_repository: Dépôt de données pour l'exécution de requêtes SQL
            document_specification: Spécification complète du document à générer
            document_context: Contexte contenant les paramètres de génération
                            (wilaya, date, période, etc.)
        """
        self._logger: Logger = get_logger(f"app.generators.{self.__class__.__name__}")
        self._logger.debug(f"Initialisation de {self.__class__.__name__}")

        self._storage_service: FileIOService = storage_service
        self._data_repository: DataRepository = data_repository
        self._document_specification: DocumentSpecification = document_specification
        self._document_context: DocumentContext = document_context
        self._workbook: Workbook | None = None

        self._logger.info(
            f"Générateur initialisé pour le document : {document_specification.display_name}"
        )
        self._logger.debug(
            f"Contexte du document : wilaya={document_context.wilaya.value}, date={document_context.report_date}"
        )

    def generate(self) -> None:
        """
        Lance le processus complet de génération du document.

        Cette méthode orchestre toutes les étapes de génération selon le
        pattern Template Method. Les étapes spécifiques au format sont
        déléguées aux sous-classes via les méthodes abstraites.

        Raises:
            FileNotFoundError: Si des fichiers requis sont manquants
            QueryExecutionError: Si l'exécution d'une requête échoue
            ValueError: Si la configuration ou les données sont invalides
            Exception: Pour toute autre erreur durant la génération
        """
        self._logger.info("Début du processus de génération du document")

        try:
            # Étape 1 : Validation des fichiers requis
            self._logger.debug("Étape 1 : Validation des fichiers requis")
            files_matching_patterns: dict[str, str] = self._validate_required_files()
            self._logger.info(
                f"Tous les fichiers requis trouvés : {list(files_matching_patterns.values())}"
            )

            # Étape 2 : Chargement des données en base de données mémoire
            self._logger.debug("Étape 2 : Chargement des données en base de données")
            self._load_data_into_db(files_matching_patterns)
            self._logger.info("Données chargées avec succès en base de données")

            # Étape 3 : Création des tables de référence
            self._logger.debug("Étape 2.5 : Création des tables de référence")
            self._create_reference_tables()
            self._logger.info("Table de référence des programmes créée avec succès")

            # Étape 4 : Exécution des requêtes
            self._logger.debug("Étape 3 : Exécution des requêtes")
            query_results: dict[str, pd.DataFrame] = self._execute_queries()
            self._logger.info(f"Exécution réussie de {len(query_results)} requêtes")

            # Étape 5 : Création du classeur et de la feuille principale
            self._logger.debug("Étape 4 : Création du classeur Excel")
            self._workbook = Workbook()
            self._workbook.remove(self._workbook.active)  # type: ignore
            sheet: Worksheet = self._workbook.create_sheet(
                self._document_specification.display_name
            )
            self._logger.info(
                f"Classeur créé avec la feuille : {self._document_specification.display_name}"
            )

            # Étape 6 : Ajout de l'en-tête (responsabilité de la sous-classe)
            self._logger.debug("Étape 5 : Ajout de l'en-tête du document")
            self._add_header(sheet)
            self._logger.debug("En-tête ajouté avec succès")

            # Étape 7 : Construction des tableaux (responsabilité de la sous-classe)
            self._logger.debug("Étape 6 : Construction du tableau principal")
            self._add_tables(sheet, query_results)
            self._logger.debug("Tableau principal construit avec succès")

            # Étape 8 : Ajout du pied de page (responsabilité de la sous-classe)
            self._logger.debug("Étape 7 : Ajout du pied de page du document")
            self._add_footer(sheet)
            self._logger.debug("Pied de page ajouté avec succès")

            # Étape 9 : Formatage final (responsabilité de la sous-classe)
            self._logger.debug("Étape 8 : Application du formatage final")
            self._finalize_formatting(sheet)
            self._logger.debug("Formatage final appliqué avec succès")

            # Étape 10 : Sauvegarde du document
            self._logger.debug("Étape 9 : Sauvegarde du document")
            self._save_document()
            self._logger.info("Génération du document terminée avec succès")

        except Exception as error:
            self._logger.exception(f"Échec de la génération du document : {error}")
            self._logger.exception("Détails complets de l'erreur")
            raise

    def _validate_required_files(self) -> dict[str, str]:
        """
        Valide la présence de tous les fichiers requis pour la génération.

        Parcourt la liste des patterns de fichiers requis définis dans la
        spécification du document et vérifie qu'un fichier correspondant
        existe pour chaque pattern.

        Returns:
            Dictionnaire mappant les noms de vues aux noms de fichiers trouvés

        Raises:
            ValueError: Si la spécification du document n'est pas définie
            FileNotFoundError: Si des fichiers requis sont manquants
        """
        self._logger.debug("Validation des fichiers requis")

        if not self._document_specification:
            error_msg: str = "Spécification du document non définie"
            self._logger.error(error_msg)
            raise ValueError(error_msg)

        missing_patterns: list[str] = []
        files_mapping: dict[str, str] = {}

        self._logger.debug(
            f"Vérification de {len(self._document_specification.required_files)} patterns de fichiers requis"
        )

        # Recherche de chaque fichier requis selon son pattern
        for pattern, table_name in self._document_specification.required_files.items():
            self._logger.debug(
                f"Recherche d'un fichier correspondant au pattern : {pattern} (vue : {table_name})"
            )
            filename: str | None = self._storage_service.find_filename_matching_pattern(
                pattern
            )
            if filename is None:
                self._logger.warning(
                    f"Aucun fichier trouvé pour le pattern : {pattern}"
                )
                missing_patterns.append(pattern)
            else:
                self._logger.info(
                    f"Fichier '{filename}' trouvé pour le pattern : {pattern}"
                )
                files_mapping[table_name] = filename

        # Vérification que tous les fichiers requis sont présents
        if missing_patterns:
            error_msg: str = (
                f"Fichiers requis manquants correspondant aux patterns : {missing_patterns}"
            )
            self._logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        self._logger.info(f"Tous les {len(files_mapping)} fichiers requis trouvés")
        return files_mapping

    def _load_data_into_db(self, files_mapping: dict[str, str]) -> None:
        """
        Charge les fichiers de données dans des vues de base de données.

        Pour chaque fichier validé, cette méthode :
        - Charge le fichier via le service de stockage
        - Nettoie les noms de colonnes (supprime les espaces)
        - Crée une vue dans le dépôt de données
        - Affiche un résumé des données chargées

        Args:
            files_mapping: Dictionnaire mappant les noms de vues aux noms de fichiers

        Raises:
            Exception: Si le chargement d'un fichier échoue
        """
        self._logger.debug("Chargement des fichiers dans les vues de base de données")

        for table_name, filename in files_mapping.items():
            self._logger.debug(
                f"Chargement du fichier '{filename}' dans la vue '{table_name}'"
            )
            try:
                # Chargement du fichier en DataFrame
                df: pd.DataFrame = self._storage_service.load_data_from_file(filename)

                # Nettoyage des noms de colonnes (suppression des espaces)
                original_columns: list[str] = list(df.columns)
                df.columns = [column.strip() for column in df.columns]
                cleaned_columns: list[str] = list(df.columns)

                if original_columns != cleaned_columns:
                    self._logger.debug(
                        f"Noms de colonnes nettoyés pour la vue '{table_name}'"
                    )

                # Création de la vue en base de données
                self._data_repository.create_table_from_dataframe(table_name, df)
                self._logger.info(
                    f"Vue '{table_name}' chargée avec succès : {len(df)} lignes"
                )

                # Affichage du résumé des données pour diagnostic
                print(self._data_repository.summarize(table_name))

            except Exception as error:
                self._logger.error(
                    f"Échec du chargement du fichier '{filename}' dans la vue '{table_name}' : {error}"
                )
                raise

    def _create_reference_tables(self) -> None:
        """
        Crée les tables de référence nécessaires à la génération du document.

        Les tables de référence contiennent des données métier statiques
        comme la liste des programmes avec leur ordre d'affichage et
        leurs consistances (nombre de logements planifiés).

        Raises:
            Exception: Si la création d'une table de référence échoue
        """
        self._logger.debug("Création des tables de référence")

        # Dictionnaire des tables de référence et de leurs fabriques
        reference_tables: dict[str, Callable[[], pd.DataFrame]] = {
            "programmes": get_programmes_dataframe,
        }

        for table_name, dataframe_factory in reference_tables.items():
            try:
                self._logger.debug(f"Création de la table de référence '{table_name}'")

                # Génération du DataFrame via la fabrique
                df: pd.DataFrame = dataframe_factory()
                self._data_repository.create_table_from_dataframe(table_name, df)

                rows, cols = df.shape
                self._logger.info(
                    f"Table de référence '{table_name}' créée : {rows} lignes et {cols} colonnes"
                )
                self._logger.debug(f"Colonnes pour '{table_name}' : {list(df.columns)}")

            except Exception as error:
                self._logger.exception(
                    f"Échec de la création de la table de référence '{table_name}' : {error}"
                )
                raise

    def _execute_queries(self) -> dict[str, pd.DataFrame]:
        """
        Exécute toutes les requêtes définies dans la spécification du document.

        Les requêtes sont formatées avec le contexte du document (date, mois, année)
        avant d'être exécutées. Les résultats sont stockés dans un dictionnaire
        pour utilisation lors de la construction des tableaux.

        Returns:
            Dictionnaire mappant les noms de requêtes aux DataFrames de résultats

        Raises:
            ValueError: Si la spécification du document n'est pas définie
            QueryExecutionError: Si l'exécution d'une requête échoue
        """
        self._logger.debug("Exécution des requêtes du document")

        if not self._document_specification:
            error_msg = "Spécification du document non définie"
            self._logger.error(error_msg)
            raise ValueError(error_msg)

        results: dict[str, pd.DataFrame] = {}
        query_count: int = len(self._document_specification.queries)
        self._logger.debug(f"Préparation de l'exécution de {query_count} requêtes")

        # Exécution de chaque requête définie dans la spécification
        for query_name, query_template in self._document_specification.queries.items():
            self._logger.debug(f"Exécution de la requête '{query_name}'")
            try:
                # Formatage de la requête avec le contexte du document
                formatted_query: str = self._format_query_with_context(query_template)
                self._logger.debug(
                    f"Requête '{query_name}' formatée avec le contexte du document"
                )

                # Exécution de la requête formatée
                result_df: pd.DataFrame = self._data_repository.execute(formatted_query)
                results[query_name] = result_df

                self._logger.info(
                    f"Requête '{query_name}' a retourné {len(result_df)} lignes"
                )

            except Exception as error:
                self._logger.exception(f"Requête '{query_name}' a échoué : {error}")
                raise QueryExecutionError(
                    f"La requête requise '{query_name}' a échoué", error
                )

        self._logger.info(f"Toutes les {query_count} requêtes exécutées avec succès")
        return results

    def _format_query_with_context(self, query_template: str) -> str:
        """
        Formate un template de requête SQL avec les valeurs du contexte du document.

        Remplace les placeholders suivants dans la requête :
        - {month_number:02d} : Numéro du mois sur 2 chiffres (ex: "03")
        - {month_number} : Numéro du mois simple (ex: "3")
        - {year} : Année complète (ex: "2024")

        Args:
            query_template: Template de requête SQL contenant des placeholders

        Returns:
            Requête SQL avec les placeholders remplacés par les valeurs réelles
        """
        self._logger.debug(
            "Formatage du template de requête avec le contexte du document"
        )

        formatted_query: str = query_template

        # Remplacement des placeholders de date si un mois est spécifié
        if self._document_context.month:
            month_number: int = self._document_context.month.number
            year: int = self._document_context.year

            # Remplacement des placeholders trouvés dans les templates de requête
            formatted_query = formatted_query.replace(
                "{month_number:02d}", f"{month_number:02d}"
            )
            formatted_query = formatted_query.replace(
                "{month_number}", str(month_number)
            )
            formatted_query = formatted_query.replace("{year}", str(year))

            self._logger.debug(
                f"Placeholders remplacés par : month_number={month_number:02d}, year={year}"
            )

        # Remplacement du placeholder d'année pour les requêtes annuelles uniquement
        formatted_query = formatted_query.replace(
            "{year}", str(self._document_context.year)
        )

        self._logger.debug("Formatage de la requête terminé")
        return formatted_query

    @abstractmethod
    def _add_header(self, sheet: Worksheet) -> None:
        """
        Ajoute l'en-tête du document à la feuille Excel.

        Cette méthode abstraite doit être implémentée par les sous-classes
        pour définir l'en-tête spécifique à chaque type de document.

        Args:
            sheet: Feuille Excel où ajouter l'en-tête
        """
        ...

    @abstractmethod
    def _add_tables(
        self, sheet: Worksheet, query_results: dict[str, pd.DataFrame]
    ) -> None:
        """
        Construit les tableaux de données du document.

        Cette méthode abstraite doit être implémentée par les sous-classes
        pour construire les tableaux spécifiques à chaque type de document
        en utilisant les résultats des requêtes.

        Args:
            sheet: Feuille Excel où ajouter les tableaux
            query_results: Résultats des requêtes indexés par nom de requête
        """
        ...

    @abstractmethod
    def _add_footer(self, sheet: Worksheet) -> None:
        """
        Ajoute le pied de page du document à la feuille Excel.

        Cette méthode abstraite doit être implémentée par les sous-classes
        pour définir le pied de page spécifique à chaque type de document.

        Args:
            sheet: Feuille Excel où ajouter le pied de page
        """
        ...

    @abstractmethod
    def _finalize_formatting(self, sheet: Worksheet) -> None:
        """
        Applique le formatage final au document.

        Cette méthode abstraite doit être implémentée par les sous-classes
        pour appliquer les styles, bordures, couleurs et autres formatages
        spécifiques à chaque type de document.

        Args:
            sheet: Feuille Excel à formater
        """
        ...

    def _save_document(self) -> None:
        """
        Sauvegarde le document Excel généré.

        Utilise le template de nom de fichier défini dans la spécification
        pour générer le nom final, en remplaçant les placeholders par les
        valeurs du contexte (wilaya, date formatée).

        Raises:
            ValueError: Si aucun classeur n'a été créé
            Exception: Si la sauvegarde échoue
        """
        self._logger.debug("Préparation de la sauvegarde du document")

        if not self._workbook:
            error_msg: str = "Aucun classeur créé"
            self._logger.error(error_msg)
            raise ValueError(error_msg)

        output_filename: str = self._document_specification.output_filename
        self._logger.debug(f"Template du nom de fichier de sortie : {output_filename}")

        # Utilisation du format de date français pour les noms de fichiers utilisateur
        output_filename = output_filename.replace(
            "{wilaya}", self._document_context.wilaya.value
        )
        output_filename = output_filename.replace(
            "{date}",
            DateFormatter.to_french_filename_date(self._document_context.report_date),
        )

        # Ajout de l'extension si nécessaire
        if not output_filename.endswith(".xlsx"):
            output_filename += ".xlsx"

        self._logger.info(f"Sauvegarde du document sous : {output_filename}")

        try:
            self._storage_service.save_data_to_file(
                data=self._workbook,
                output_filename=output_filename,
            )
            self._logger.info(f"Document sauvegardé avec succès : {output_filename}")
        except Exception as error:
            self._logger.exception(f"Échec de la sauvegarde du document : {error}")
            raise
