from __future__ import annotations

"""
Fabrique pour la création de contextes de documents.

Ce module implémente le pattern Factory pour créer des instances
de DocumentContext selon différentes périodicités (mensuelle,
semestrielle, annuelle) avec des paramètres par défaut appropriés.

La fabrique simplifie la création de contextes en gérant
automatiquement les valeurs par défaut et la logique
de génération des dates de rapport.
"""

# Imports de la bibliothèque standard
from datetime import date
from logging import Logger

# Imports de l'application locale
from app.services.document_generation.models.document_context import (
    DocumentContext,
)
from app.services.document_generation.enums.space_time import Periodicity, Month, Wilaya
from app.utils.logging_setup import get_logger


class DocumentContextFactory(object):
    """
    Fabrique pour la création de contextes de documents.

    Cette classe implémente le pattern Factory pour créer des instances
    de DocumentContext avec la logique appropriée selon la périodicité.
    Elle gère automatiquement les valeurs par défaut et les calculs
    de dates de fin de période.

    La classe ne peut pas être instanciée - toutes les méthodes
    sont des méthodes de classe statiques.

    Exemples:
        Contexte mensuel :
        >>> context = DocumentContextFactory.create_context(
        ...     wilaya=Wilaya.ALGER,
        ...     periodicity=Periodicity.MONTHLY,
        ...     year=2024,
        ...     month=Month.JANVIER
        ... )

        Contexte annuel avec valeurs par défaut :
        >>> context = DocumentContextFactory.create_context(
        ...     wilaya=Wilaya.CONSTANTINE,
        ...     periodicity=Periodicity.ANNUAL
        ... )  # Utilise l'année courante et le 31 décembre
    """

    __slots__ = ()

    _logger: Logger = get_logger("app.services.context_factory")

    def __new__(cls):
        """
        Empêche l'instanciation de la classe.

        Raises:
            RuntimeError: Toujours levée car cette classe ne doit pas être instanciée
        """
        raise RuntimeError(
            "DocumentContextFactory ne peut pas être instanciée. Utilisez les méthodes de classe."
        )

    @classmethod
    def create_context(
        cls,
        wilaya: Wilaya,
        year: int | None = None,
        periodicity: Periodicity | None = None,
        month: Month | None = None,
        semester: int | None = None,
        report_date: date | None = None,
    ) -> DocumentContext:
        """
        Crée un contexte de document selon la périodicité spécifiée.

        Cette méthode orchestre la création du contexte en déléguant
        à la méthode spécialisée selon la périodicité demandée.

        Args:
            wilaya: Wilaya concernée par le document
            year: Année du rapport (défaut: année courante)
            periodicity: Périodicité du document (défaut: mensuel)
            month: Mois pour les rapports mensuels
            semester: Semestre pour les rapports semestriels
            report_date: Date spécifique du rapport

        Returns:
            Instance de DocumentContext configurée selon les paramètres

        Raises:
            ValueError: Si la périodicité n'est pas supportée
        """
        cls._logger.info(
            f"Création du contexte de document pour la wilaya : {wilaya.value}"
        )
        cls._logger.debug(
            f"Paramètres : année={year}, périodicité={periodicity}, mois={month}, semestre={semester}, date_rapport={report_date}"
        )

        periodicity = periodicity or Periodicity.MONTHLY
        cls._logger.debug(f"Utilisation de la périodicité : {periodicity.value}")

        try:
            match periodicity:
                case Periodicity.MONTHLY:
                    cls._logger.debug("Création d'un contexte de document mensuel")
                    context = cls._monthly(wilaya, year, month, report_date)
                case Periodicity.SEMIANNUAL:
                    cls._logger.debug("Création d'un contexte de document semestriel")
                    context = cls._semiannual(wilaya, year, semester, report_date)
                case Periodicity.ANNUAL:
                    cls._logger.debug("Création d'un contexte de document annuel")
                    context = cls._annual(wilaya, year, report_date)
                case _:
                    error_msg = f"Périodicité inconnue : {periodicity}"
                    cls._logger.error(error_msg)
                    raise ValueError(error_msg)

            cls._logger.info(
                f"Contexte {periodicity.value} créé avec succès pour {wilaya.value} - {context.report_date}"
            )
            return context

        except Exception as error:
            cls._logger.error(f"Échec de la création du contexte de document : {error}")
            raise

    @staticmethod
    def _monthly(
        wilaya: Wilaya, year: int | None, month: Month | None, report_date: date | None
    ) -> DocumentContext:
        """
        Crée un contexte de document pour une périodicité mensuelle.

        Génère automatiquement la date de fin de mois si aucune date
        spécifique n'est fournie. Utilise le mois et l'année courants
        par défaut.

        Args:
            wilaya: Wilaya concernée par le document
            year: Année du rapport (défaut: année courante)
            month: Mois du rapport (défaut: mois courant)
            report_date: Date spécifique du rapport (défaut: fin de mois)

        Returns:
            Contexte mensuel configuré avec les paramètres fournis
        """
        logger: Logger = DocumentContextFactory._logger
        logger.debug("Traitement des paramètres de contexte mensuel")

        today: date = date.today()
        year = year or today.year
        month = month or Month.from_number(today.month)

        logger.debug(f"Année résolue : {year}, mois : {month.value}")

        if report_date is None:
            # Par défaut, utiliser la fin du mois
            last_day: int = month.last_day(year)
            report_date = date(year, month.number, last_day)
            logger.debug(
                f"Date de rapport générée par défaut : {report_date} (fin de {month.value})"
            )
        else:
            logger.debug(f"Utilisation de la date de rapport fournie : {report_date}")

        context = DocumentContext(
            wilaya=wilaya,
            year=year,
            report_date=report_date,
            month=month,
        )

        logger.info(f"Contexte mensuel créé : {wilaya.value}, {month.value} {year}")
        return context

    @staticmethod
    def _semiannual(
        wilaya: Wilaya, year: int | None, semester: int | None, report_date: date | None
    ) -> DocumentContext:
        """
        Crée un contexte de document pour une périodicité semestrielle.

        Génère automatiquement la date de fin de semestre (30 juin ou 31 décembre)
        si aucune date spécifique n'est fournie. Détermine le semestre courant
        selon la date actuelle.

        Args:
            wilaya: Wilaya concernée par le document
            year: Année du rapport (défaut: année courante)
            semester: Semestre du rapport (défaut: semestre courant)
            report_date: Date spécifique du rapport (défaut: fin de semestre)

        Returns:
            Contexte semestriel configuré avec les paramètres fournis
        """
        logger: Logger = DocumentContextFactory._logger
        logger.debug("Traitement des paramètres de contexte semestriel")

        today: date = date.today()
        year = year or today.year
        semester = semester or (1 if today.month <= 6 else 2)

        logger.debug(f"Année résolue : {year}, semestre : {semester}")

        if report_date is None:
            # Par défaut, utiliser la fin du semestre
            end_month_number = 6 if semester == 1 else 12
            last_day: int = Month.from_number(end_month_number).last_day(year)
            report_date = date(year, end_month_number, last_day)
            logger.debug(
                f"Date de rapport générée par défaut : {report_date} (fin du semestre {semester})"
            )
        else:
            logger.debug(f"Utilisation de la date de rapport fournie : {report_date}")

        context: DocumentContext = DocumentContext(
            wilaya=wilaya, year=year, semester=semester, report_date=report_date
        )

        logger.info(
            f"Contexte semestriel créé : {wilaya.value}, semestre {semester} de {year}"
        )
        return context

    @staticmethod
    def _annual(
        wilaya: Wilaya, year: int | None, report_date: date | None
    ) -> DocumentContext:
        """
        Crée un contexte de document pour une périodicité annuelle.

        Génère automatiquement la date de fin d'année (31 décembre)
        si aucune date spécifique n'est fournie. Utilise l'année
        courante par défaut.

        Args:
            wilaya: Wilaya concernée par le document
            year: Année du rapport (défaut: année courante)
            report_date: Date spécifique du rapport (défaut: 31 décembre)

        Returns:
            Contexte annuel configuré avec les paramètres fournis
        """
        logger: Logger = DocumentContextFactory._logger
        logger.debug("Traitement des paramètres de contexte annuel")

        today: date = date.today()
        year = year or today.year

        logger.debug(f"Année résolue : {year}")

        if report_date is None:
            report_date = date(year, 12, 31)
            logger.debug(
                f"Date de rapport générée par défaut : {report_date} (fin d'année)"
            )
        else:
            logger.debug(f"Utilisation de la date de rapport fournie : {report_date}")

        context: DocumentContext = DocumentContext(
            wilaya=wilaya, year=year, report_date=report_date
        )

        logger.info(f"Contexte annuel créé : {wilaya.value}, année {year}")
        return context
