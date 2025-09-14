from __future__ import annotations

# Imports de la bibliothèque standard
from pathlib import Path
import re
from typing import Any
from logging import Logger

# Imports tiers
import pandas as pd
from openpyxl import Workbook

# Imports de l'application locale
from app.utils.exceptions import DataLoadError
from app.config import FileIOConfig
from app.utils.logging_setup import get_logger


class FileIOService(object):
    """
    Service de gestion des entrées/sorties de fichiers.

    Cette classe encapsule toutes les opérations de lecture et d'écriture
    de fichiers, avec validation des formats, tailles et extensions.
    Utilise __slots__ pour optimiser l'utilisation mémoire.
    """

    __slots__ = ("_config", "_logger")

    def __init__(self, storage_config: FileIOConfig) -> None:
        """
        Initialise le service IO avec la configuration de stockage fournie.

        Args:
            storage_config: Configuration contenant les répertoires et contraintes
                           pour les fichiers d'entrée et de sortie
        """
        self._logger: Logger = get_logger("app.services.file_storage")
        self._logger.debug("Initialisation du service de stockage de fichiers")

        self._config: FileIOConfig = storage_config

        self._logger.info(
            f"Service de stockage de fichiers initialisé - uploads : {self._config.uploads_dir}, résultats : {self._config.results_dir}"
        )
        self._logger.debug(
            f"Configuration - Taille max : {self._config.max_input_file_size_mb}MB, Extensions autorisées : {self._config.allowed_input_file_extensions}"
        )

    def load_data_from_file(self, filename: str) -> pd.DataFrame:
        """
        Charge les données d'un fichier Excel vers un DataFrame pandas.

        Cette méthode effectue plusieurs vérifications :
        - Existence du fichier
        - Extension autorisée
        - Taille du fichier
        - Détection automatique de la ligne de début des données

        Args:
            filename: Nom du fichier à charger (dans le répertoire uploads)

        Returns:
            DataFrame pandas contenant les données du fichier

        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            ValueError: Si l'extension ou la taille n'est pas valide
            DataLoadError: Si le chargement échoue pour une autre raison
        """
        self._logger.info(f"Chargement des données depuis le fichier : {filename}")
        file_path: Path = self._config.uploads_dir / filename
        self._logger.debug(f"Chemin complet du fichier : {file_path}")

        # Vérifications préliminaires du fichier
        self._verify_file_exists(file_path)
        self._verify_input_extension(file_path)
        self._verify_file_size(file_path)

        try:
            # Détection automatique de la ligne de début du tableau
            self._logger.debug(
                "Analyse du fichier pour trouver la ligne de début du tableau"
            )
            skiprows: int = self._find_table_start_row(file_path)
            self._logger.debug(f"Le tableau commence à la ligne {skiprows}")

            # Lecture du fichier Excel avec pandas
            self._logger.debug("Lecture du fichier Excel avec pandas")
            dataframe: pd.DataFrame = pd.read_excel(  # type: ignore
                file_path, dtype_backend="numpy_nullable", skiprows=skiprows
            )

            self._logger.info(
                f"Chargement réussi : {len(dataframe)} lignes et {len(dataframe.columns)} colonnes depuis {filename}"
            )
            self._logger.debug(f"Noms des colonnes : {list(dataframe.columns)}")

            return dataframe
        except Exception as error:
            self._logger.exception(
                f"Échec du chargement des données depuis {filename} : {error}"
            )
            raise DataLoadError(file_path, error) from error

    def save_data_to_file(self, data: Any, output_filename: str) -> None:
        """
        Sauvegarde les données vers un fichier de sortie.

        Actuellement supporte uniquement les objets Workbook d'openpyxl
        pour la génération de fichiers Excel.

        Args:
            data: Données à sauvegarder (doit être un objet Workbook)
            output_filename: Nom du fichier de sortie (dans le répertoire results)

        Raises:
            ValueError: Si le type de données n'est pas supporté ou
                       si l'extension n'est pas valide
        """
        self._logger.info(f"Sauvegarde des données vers le fichier : {output_filename}")
        output_path: Path = self._config.results_dir / output_filename
        self._logger.debug(f"Chemin complet de sortie : {output_path}")

        # Vérification de l'extension de sortie
        self._verify_output_extension(output_filename)

        try:
            if isinstance(data, Workbook):
                self._logger.debug("Sauvegarde du classeur Excel")
                data.save(output_path)
                self._logger.info(
                    f"Classeur sauvegardé avec succès vers {output_filename}"
                )
            else:
                self._logger.error(
                    f"Type de données non supporté pour la sauvegarde : {type(data)}"
                )
                raise ValueError(
                    f"Impossible de sauvegarder des données de type {type(data)}"
                )
        except Exception as error:
            self._logger.exception(
                f"Échec de la sauvegarde vers {output_filename} : {error}"
            )
            raise

    def find_filename_matching_pattern(self, pattern: str) -> str | None:
        """
        Recherche un fichier correspondant à un pattern regex dans le répertoire uploads.

        Cette méthode est utile pour trouver des fichiers avec des noms dynamiques
        ou pour valider la présence d'un fichier avec un format spécifique.

        Args:
            pattern: Expression régulière pour la recherche de fichier

        Returns:
            Nom du fichier correspondant, ou None si aucun fichier trouvé

        Raises:
            ValueError: Si le pattern regex est invalide ou si plusieurs fichiers correspondent
        """
        self._logger.debug(
            f"Recherche de fichiers correspondant au pattern : {pattern}"
        )

        # Validation du pattern regex
        try:
            regex: re.Pattern[str] = re.compile(pattern)
        except re.error as error:
            self._logger.exception(f"Pattern regex invalide '{pattern}' : {error}")
            raise ValueError(f"Pattern regex invalide : {pattern}") from error

        # Recherche dans le répertoire uploads
        self._logger.debug(f"Analyse du répertoire : {self._config.uploads_dir}")
        matches: list[str] = [
            element.name
            for element in self._config.uploads_dir.iterdir()
            if element.is_file() and regex.match(element.name)
        ]

        self._logger.debug(f"Trouvé {len(matches)} fichiers correspondants : {matches}")

        # Gestion des cas de résultat
        if not matches:
            self._logger.warning(
                f"Aucun fichier trouvé correspondant au pattern : {pattern}"
            )
            return None

        if len(matches) > 1:
            error_msg = (
                f"Plusieurs fichiers correspondent au pattern {pattern!r} : {matches}"
            )
            self._logger.error(error_msg)
            raise ValueError(error_msg)

        matched_file: str = matches[0]
        self._logger.info(f"Fichier correspondant trouvé : {matched_file}")
        return matched_file

    def _verify_file_exists(self, file_path: Path) -> None:
        """
        Vérifie l'existence du fichier spécifié.

        Args:
            file_path: Chemin vers le fichier à vérifier

        Raises:
            FileNotFoundError: Si le fichier n'existe pas
        """
        self._logger.debug(f"Vérification de l'existence du fichier : {file_path}")
        if not file_path.exists():
            error_msg: str = f"Fichier non trouvé : {file_path}"
            self._logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        self._logger.debug("Le fichier existe")

    def _verify_input_extension(self, file_path: Path) -> None:
        """
        Vérifie que l'extension du fichier d'entrée est autorisée.

        Args:
            file_path: Chemin vers le fichier à vérifier

        Raises:
            ValueError: Si l'extension n'est pas dans la liste des extensions autorisées
        """
        extension: str = file_path.suffix.lstrip(".").lower()
        self._logger.debug(f"Vérification de l'extension du fichier : .{extension}")

        if extension not in self._config.allowed_input_file_extensions:
            error_msg: str = (
                f"Extension '.{extension}' non autorisée. "
                f"Autorisées : {self._config.allowed_input_file_extensions}"
            )
            self._logger.error(error_msg)
            raise ValueError(error_msg)
        self._logger.debug("Extension du fichier valide")

    def _verify_file_size(self, file_path: Path) -> None:
        """
        Vérifie que la taille du fichier ne dépasse pas la limite configurée.

        Args:
            file_path: Chemin vers le fichier à vérifier

        Raises:
            ValueError: Si le fichier dépasse la taille maximale autorisée
        """
        size_bytes = file_path.stat().st_size
        size_mb: float = size_bytes / (1024 * 1024)
        self._logger.debug(f"Vérification de la taille du fichier : {size_mb:.2f} MB")

        if size_mb > self._config.max_input_file_size_mb:
            error_msg: str = (
                f"Le fichier {file_path} est trop volumineux ({size_mb:.2f} MB). "
                f"Taille max autorisée : {self._config.max_input_file_size_mb} MB"
            )
            self._logger.error(error_msg)
            raise ValueError(error_msg)
        self._logger.debug("Taille du fichier dans les limites autorisées")

    def _verify_output_extension(self, output_filename: str) -> None:
        """
        Vérifie que l'extension du fichier de sortie correspond au format par défaut.

        Args:
            output_filename: Nom du fichier de sortie à vérifier

        Raises:
            ValueError: Si l'extension ne correspond pas au format de sortie par défaut
        """
        extension: str = Path(output_filename).suffix.lstrip(".").lower()
        self._logger.debug(f"Vérification de l'extension de sortie : .{extension}")

        if extension != self._config.default_output_format:
            error_msg: str = (
                f"Le format de sortie '.{extension}' ne correspond pas au format de sortie par défaut "
                f"'{self._config.default_output_format}'"
            )
            self._logger.error(error_msg)
            raise ValueError(error_msg)
        self._logger.debug("Extension de sortie valide")

    def _find_table_start_row(self, file_path: Path) -> int:
        """
        Trouve automatiquement la ligne où commence le tableau de données.

        Cette méthode recherche l'en-tête spécifique "N° d'ordre" pour déterminer
        où commencent les données réelles dans le fichier Excel, permettant
        d'ignorer les métadonnées et en-têtes qui peuvent précéder le tableau.

        Args:
            file_path: Chemin vers le fichier Excel à analyser

        Returns:
            Index de la ligne où commence le tableau (0-indexé)

        Raises:
            DataLoadError: Si l'en-tête "N° d'ordre" n'est pas trouvé ou
                          si la lecture préliminaire du fichier échoue
        """
        self._logger.debug(
            "Recherche de la ligne de début du tableau en cherchant l'en-tête 'N° d'ordre'"
        )

        try:
            # Lecture des premières lignes pour analyse
            preview_df: pd.DataFrame = pd.read_excel(file_path, nrows=30, header=None)  # type: ignore
            self._logger.debug(f"Chargement de {len(preview_df)} lignes d'aperçu")
        except Exception as error:
            self._logger.exception(
                f"Échec de la lecture de l'aperçu du fichier : {error}"
            )
            raise DataLoadError(file_path, error) from error

        # Recherche de l'en-tête "N° d'ordre" dans les premières cellules de chaque ligne
        for row_idx, (_, row) in enumerate(preview_df.iterrows()):
            first_cell: str = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            self._logger.debug(
                f"Ligne {row_idx} : '{first_cell[:50]}{'...' if len(first_cell) > 50 else ''}'"
            )

            if "N° d'ordre" in first_cell:
                self._logger.info(
                    f"En-tête du tableau 'N° d'ordre' trouvé à la ligne {row_idx}"
                )
                return row_idx

        # Si l'en-tête n'est pas trouvé, lever une erreur
        error_msg: str = (
            "Impossible de trouver l'en-tête 'N° d'ordre' pour déterminer le début du tableau"
        )
        self._logger.error(error_msg)
        raise DataLoadError(file_path, Exception(error_msg))
