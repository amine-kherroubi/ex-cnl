from __future__ import annotations

# Imports de la bibliothèque standard
from pathlib import Path
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
            storage_config: Configuration contenant les contraintes
                           pour les fichiers d'entrée et de sortie
        """
        self._logger: Logger = get_logger("app.services.file_io_service")
        self._logger.debug("Initialisation du service de stockage de fichiers")

        self._config: FileIOConfig = storage_config

        self._logger.info("Service de stockage de fichiers initialisé")
        self._logger.debug(
            f"Extensions autorisées : {self._config.allowed_source_file_extensions}"
        )

    def load_data_from_file(self, source_file_path: Path) -> pd.DataFrame:
        """
        Charge les données d'un fichier Excel vers un DataFrame pandas.

        Note: File existence is validated by the controller layer.
        This method assumes the file exists and is readable.

        Args:
            source_file_path: Chemin complet vers le fichier à charger

        Returns:
            DataFrame pandas contenant les données du fichier

        Raises:
            DataLoadError: Si le chargement échoue pour une raison quelconque
        """
        self._logger.info(
            f"Chargement des données depuis le fichier : {source_file_path}"
        )

        try:
            # Détection automatique de la ligne de début du tableau
            self._logger.debug(
                "Analyse du fichier pour trouver la ligne de début du tableau"
            )
            skiprows: int = self._find_table_start_row(source_file_path)
            self._logger.debug(f"Le tableau commence à la ligne {skiprows}")

            # Lecture du fichier Excel avec pandas
            self._logger.debug("Lecture du fichier Excel avec pandas")
            dataframe: pd.DataFrame = pd.read_excel(  # type: ignore
                source_file_path, dtype_backend="numpy_nullable", skiprows=skiprows
            )

            self._logger.info(
                f"Chargement réussi : {len(dataframe)} lignes et {len(dataframe.columns)} colonnes depuis {source_file_path.name}"
            )
            self._logger.debug(f"Noms des colonnes : {list(dataframe.columns)}")

            return dataframe
        except Exception as error:
            self._logger.exception(
                f"Échec du chargement des données depuis {source_file_path} : {error}"
            )
            raise DataLoadError(source_file_path, error) from error

    def save_data_to_file(self, data: Any, output_file_path: Path) -> None:
        """
        Sauvegarde les données vers un fichier de sortie.

        Args:
            data: Données à sauvegarder (doit être un objet Workbook)
            output_file_path: Chemin complet du fichier de sortie

        Raises:
            ValueError: Si le type de données n'est pas supporté
        """
        self._logger.info(
            f"Sauvegarde des données vers le fichier : {output_file_path}"
        )

        try:
            if isinstance(data, Workbook):
                self._logger.debug("Sauvegarde du classeur Excel")
                # Ensure parent directory exists
                output_file_path.parent.mkdir(parents=True, exist_ok=True)
                data.save(output_file_path)
                self._logger.info(
                    f"Classeur sauvegardé avec succès vers {output_file_path}"
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
                f"Échec de la sauvegarde vers {output_file_path} : {error}"
            )
            raise

    def _find_table_start_row(self, source_file_path: Path) -> int:
        """
        Trouve automatiquement la ligne où commence le tableau de données.

        Cette méthode recherche l'en-tête spécifique "N° d'ordre" pour déterminer
        où commencent les données réelles dans le fichier Excel, permettant
        d'ignorer les métadonnées et en-têtes qui peuvent précéder le tableau.

        Args:
            source_file_path: Chemin vers le fichier Excel à analyser

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
            preview_df: pd.DataFrame = pd.read_excel(source_file_path, nrows=30, header=None)  # type: ignore
            self._logger.debug(f"Chargement de {len(preview_df)} lignes d'aperçu")
        except Exception as error:
            self._logger.exception(
                f"Échec de la lecture de l'aperçu du fichier : {error}"
            )
            raise DataLoadError(source_file_path, error) from error

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
        raise DataLoadError(source_file_path, Exception(error_msg))
