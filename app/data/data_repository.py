from __future__ import annotations

# Imports de la bibliothèque standard
from typing import Any, Protocol
from logging import Logger

# Imports tiers
import duckdb
import pandas as pd

# Imports de l'application locale
from app.utils.exceptions import DatabaseError, QueryExecutionError
from app.config import DatabaseConfig
from app.utils.logging_setup import get_logger


class DataRepository(Protocol):
    """
    Protocol définissant l'interface pour les dépôts de données.

    Utilise le pattern Repository pour abstraire l'accès aux données
    et permettre une implémentation modulaire avec différents backends.
    """

    def create_table_from_dataframe(
        self,
        table_name: str,
        dataframe: pd.DataFrame,
    ) -> None:
        """
        Crée une vue dans la base de données à partir d'un DataFrame pandas.

        Args:
            table_name: Nom de la vue à créer
            dataframe: DataFrame pandas contenant les données
        """
        ...

    def execute(self, query: str) -> pd.DataFrame:
        """
        Exécute une requête SQL et retourne le résultat sous forme de DataFrame.

        Args:
            query: Requête SQL à exécuter

        Returns:
            DataFrame pandas contenant les résultats de la requête
        """
        ...

    def count_records(self, table_name: str) -> int:
        """
        Compte le nombre d'enregistrements dans une vue.

        Args:
            table_name: Nom de la vue

        Returns:
            Nombre total d'enregistrements
        """
        ...

    def describe(self, table_name: str) -> pd.DataFrame:
        """
        Décrit la structure d'une vue (colonnes, types, etc.).

        Args:
            table_name: Nom de la vue à décrire

        Returns:
            DataFrame décrivant la structure de la vue
        """
        ...

    def get_data(
        self,
        table_name: str,
        offset: int = 0,
        limit: int = 5,
    ) -> pd.DataFrame:
        """
        Récupère un échantillon de données d'une vue avec pagination.

        Args:
            table_name: Nom de la vue
            offset: Nombre d'enregistrements à ignorer (défaut: 0)
            limit: Nombre maximum d'enregistrements à retourner (défaut: 5)

        Returns:
            DataFrame contenant l'échantillon de données
        """
        ...

    def summarize(self, table_name: str) -> dict[str, Any]:
        """
        Génère un résumé complet d'une vue.

        Args:
            table_name: Nom de la vue à résumer

        Returns:
            Dictionnaire contenant le résumé de la vue
        """
        ...

    def close(self) -> None:
        """Ferme la connexion à la base de données."""
        ...


class DuckDBRepository:
    """
    Implémentation du pattern Repository utilisant DuckDB.

    Cette classe encapsule toutes les interactions avec DuckDB et fournit
    une interface haut niveau pour les opérations de base de données.
    Utilise __slots__ pour optimiser l'utilisation mémoire.
    """

    __slots__ = (
        "_config",
        "_connection",
        "_data_loaded",
        "_logger",
    )

    def __init__(self, db_config: DatabaseConfig) -> None:
        """
        Initialise le dépôt DuckDB avec la configuration fournie.

        Args:
            db_config: Configuration de la base de données

        Raises:
            DatabaseError: Si l'initialisation de la connexion échoue
        """
        self._logger: Logger = get_logger("app.data.repository")
        self._logger.debug("Initialisation du dépôt DuckDB")

        self._config: DatabaseConfig = db_config

        # Configuration de DuckDB avec les paramètres fournis
        config_dict: dict[str, Any] = {
            "max_memory": db_config.max_memory if db_config.max_memory else "1GB",
        }
        self._logger.debug(f"Configuration DuckDB : {config_dict}")

        # Création de la connexion selon le type (fichier ou mémoire)
        self._connection: duckdb.DuckDBPyConnection | None
        if db_config.path:
            self._logger.info(f"Connexion au fichier DuckDB : {db_config.path}")
            self._connection = duckdb.connect(database=db_config.path, config=config_dict)  # type: ignore
        else:
            self._logger.info("Création d'une connexion DuckDB en mémoire")
            self._connection = duckdb.connect(database=":memory:", config=config_dict)  # type: ignore

        # Activation du logging des requêtes si demandé
        if db_config.enable_logging:
            if not self._connection:
                error_msg: str = "Échec de l'initialisation de la connexion DuckDB"
                self._logger.error(error_msg)
                raise DatabaseError(error_msg)
            self._logger.debug("Activation du logging des requêtes DuckDB")
            self._connection.execute("PRAGMA enable_logging;")

        self._data_loaded: bool = False
        self._logger.info("Dépôt DuckDB initialisé avec succès")

    def create_table_from_dataframe(
        self, table_name: str, dataframe: pd.DataFrame
    ) -> None:
        """
        Crée une vue DuckDB à partir d'un DataFrame pandas.

        Cette méthode enregistre le DataFrame comme une vue temporaire
        dans DuckDB, permettant d'effectuer des requêtes SQL dessus.

        Args:
            table_name: Nom de la vue à créer dans DuckDB
            dataframe: DataFrame pandas contenant les données à importer

        Raises:
            DatabaseError: Si la connexion est fermée ou si l'opération échoue
        """
        self._logger.debug(
            f"Création de la vue '{table_name}' à partir d'un DataFrame de forme {dataframe.shape}"
        )

        if not self._connection:
            error_msg: str = "La connexion est fermée"
            self._logger.error(error_msg)
            raise DatabaseError(error_msg)

        try:
            # Enregistrement du DataFrame comme vue dans DuckDB
            self._connection.register(table_name, dataframe)
            self._data_loaded = True
            rows, cols = dataframe.shape
            self._logger.info(
                f"Vue '{table_name}' créée avec succès : {rows} lignes et {cols} colonnes"
            )

        except Exception as error:
            error_msg: str = f"Échec de la création de la vue '{table_name}' : {error}"
            self._logger.exception(error_msg)
            raise DatabaseError(error_msg) from error

    def execute(self, query: str) -> pd.DataFrame:
        """
        Exécute une requête SQL et retourne le résultat sous forme de DataFrame.

        Cette méthode est le point d'entrée principal pour l'exécution
        de requêtes SQL sur les vues créées dans DuckDB.

        Args:
            query: Requête SQL à exécuter

        Returns:
            DataFrame pandas contenant les résultats de la requête

        Raises:
            DatabaseError: Si la connexion est fermée ou aucune donnée n'est chargée
            QueryExecutionError: Si l'exécution de la requête échoue
        """
        self._logger.debug(
            f"Exécution de la requête : {query[:100]}{'...' if len(query) > 100 else ''}"
        )

        if not self._connection:
            error_msg: str = "La connexion est fermée"
            self._logger.error(error_msg)
            raise DatabaseError(error_msg)

        if not self._data_loaded:
            error_msg: str = "Aucune donnée chargée dans le dépôt"
            self._logger.error(error_msg)
            raise DatabaseError(error_msg)

        try:
            # Exécution de la requête et conversion en DataFrame
            result: pd.DataFrame = self._connection.execute(query).fetchdf()
            self._logger.debug(
                f"Requête retournée : {len(result)} lignes et {len(result.columns)} colonnes"
            )
            return result
        except Exception as error:
            self._logger.exception(f"Échec de l'exécution de la requête : {error}")
            raise QueryExecutionError(query, error) from error

    def count_records(self, table_name: str) -> int:
        """
        Compte le nombre total d'enregistrements dans une vue.

        Args:
            table_name: Nom de la vue à analyser

        Returns:
            Nombre total d'enregistrements dans la vue
        """
        self._logger.debug(f"Comptage des enregistrements dans la vue '{table_name}'")
        result: pd.DataFrame = self.execute(
            f"SELECT COUNT(*) as total_rows FROM {table_name}"
        )
        count: int = int(result["total_rows"].iloc[0])
        self._logger.debug(f"La vue '{table_name}' contient {count} enregistrements")
        return count

    def describe(self, table_name: str) -> pd.DataFrame:
        """
        Décrit la structure d'une vue (colonnes, types de données, etc.).

        Args:
            table_name: Nom de la vue à décrire

        Returns:
            DataFrame contenant la description de la structure de la vue
        """
        self._logger.debug(f"Description de la structure de la vue '{table_name}'")
        result: pd.DataFrame = self.execute(f"DESCRIBE {table_name}")
        self._logger.debug(f"La vue '{table_name}' a {len(result)} colonnes")
        return result

    def get_data(
        self, table_name: str, offset: int = 0, limit: int = 5
    ) -> pd.DataFrame:
        """
        Récupère un échantillon de données d'une vue avec pagination.

        Cette méthode est utile pour examiner les données sans charger
        l'ensemble complet, particulièrement pour de gros datasets.

        Args:
            table_name: Nom de la vue à échantillonner
            offset: Nombre d'enregistrements à ignorer depuis le début (défaut: 0)
            limit: Nombre maximum d'enregistrements à retourner (défaut: 5)

        Returns:
            DataFrame contenant l'échantillon de données demandé
        """
        self._logger.debug(
            f"Récupération d'un échantillon de la vue '{table_name}' (offset={offset}, limit={limit})"
        )
        result: pd.DataFrame = self.execute(
            f"SELECT * FROM {table_name} OFFSET {offset} LIMIT {limit}"
        )
        self._logger.debug(
            f"Récupération de {len(result)} lignes d'échantillon de la vue '{table_name}'"
        )
        return result

    def summarize(self, table_name: str) -> dict[str, Any]:
        """
        Génère un résumé complet d'une vue incluant statistiques et échantillon.

        Le résumé inclut :
        - Le nombre total d'enregistrements
        - La description de la structure (colonnes, types)
        - Un échantillon des données

        Args:
            table_name: Nom de la vue à résumer

        Returns:
            Dictionnaire contenant :
            - 'total_records': nombre total d'enregistrements
            - 'table_description': structure de la table
            - 'sample_data': échantillon des données
            Retourne un dictionnaire vide en cas d'erreur
        """
        self._logger.debug(f"Génération du résumé pour la vue '{table_name}'")
        try:
            summary: dict[str, Any] = {
                "total_records": self.count_records(table_name),
                "table_description": self.describe(table_name),
                "sample_data": self.get_data(table_name),
            }
            self._logger.info(
                f"Résumé généré pour la vue '{table_name}' avec {summary['total_records']} enregistrements"
            )
            return summary
        except Exception as error:
            self._logger.exception(
                f"Échec de la génération du résumé pour la vue '{table_name}' : {error}"
            )
            return {}

    def close(self) -> None:
        """
        Ferme proprement la connexion à la base de données.

        Cette méthode doit être appelée pour libérer les ressources
        et s'assurer que tous les changements sont persistés.
        """
        if not self._connection:
            self._logger.debug("Connexion déjà fermée")
            return

        self._logger.info("Fermeture de la connexion DuckDB")
        self._connection.close()
        self._connection = None
        self._logger.debug("Connexion DuckDB fermée avec succès")
