from __future__ import annotations

"""
Énumérations pour les dimensions spatiales et temporelles.

Ce module définit les énumérations utilisées pour représenter
les divisions administratives algériennes (wilayas), les mois
en français et les périodicités de génération de documents.

Ces énumérations garantissent la cohérence des données spatiales
et temporelles à travers l'application.
"""

# Imports de la bibliothèque standard
from calendar import monthrange
from enum import StrEnum


class Wilaya(StrEnum):
    """
    Énumération des 58 wilayas (divisions administratives) d'Algérie.

    Chaque wilaya correspond à une subdivision territoriale officielle
    de l'Algérie. Cette énumération utilise les noms français officiels
    et fournit des méthodes utilitaires pour obtenir les codes numériques
    et identifier les wilayas du sud.

    Exemples:
        >>> wilaya = Wilaya.ALGER
        >>> print(wilaya.value)  # "Alger"
        >>> print(wilaya.code)  # 16
        >>> print(wilaya.is_south())  # False
    """

    ADRAR = "Adrar"
    CHLEF = "Chlef"
    LAGHOUAT = "Laghouat"
    OUM_EL_BOUAGHI = "Oum El Bouaghi"
    BATNA = "Batna"
    BEJAIA = "Béjaïa"
    BISKRA = "Biskra"
    BECHAR = "Béchar"
    BLIDA = "Blida"
    BOUIRA = "Bouira"
    TAMANRASSET = "Tamanrasset"
    TEBESSA = "Tébessa"
    TLEMCEN = "Tlemcen"
    TIARET = "Tiaret"
    TIZI_OUZOU = "Tizi Ouzou"
    ALGER = "Alger"
    DJELFA = "Djelfa"
    JIJEL = "Jijel"
    SETIF = "Sétif"
    SAIDA = "Saïda"
    SKIKDA = "Skikda"
    SIDI_BEL_ABBES = "Sidi Bel Abbès"
    ANNABA = "Annaba"
    GUELMA = "Guelma"
    CONSTANTINE = "Constantine"
    MEDEA = "Médéa"
    MOSTAGANEM = "Mostaganem"
    MSILA = "M'Sila"
    MASCARA = "Mascara"
    OUARGLA = "Ouargla"
    ORAN = "Oran"
    EL_BAYADH = "El Bayadh"
    ILLIZI = "Illizi"
    BORDJ_BOU_ARRERIDJ = "Bordj Bou Arréridj"
    BOUMERDES = "Boumerdès"
    EL_TARF = "El Tarf"
    TINDOUF = "Tindouf"
    TISSEMSILT = "Tissemsilt"
    EL_OUED = "El Oued"
    KHENCHELA = "Khenchela"
    SOUK_AHRAS = "Souk Ahras"
    TIPAZA = "Tipaza"
    MILA = "Mila"
    AIN_DEFLA = "Aïn Defla"
    NAAMA = "Naâma"
    AIN_TEMOUCHENT = "Aïn Témouchent"
    GHARDAIA = "Ghardaïa"
    RELIZANE = "Relizane"
    TIMIMOUN = "Timimoun"
    BORDJ_BADJI_MOKHTAR = "Bordj Badji Mokhtar"
    OUED_EL_MAOU = "Ouled Djellal"
    BENI_ABBES = "Béni Abbès"
    IN_SALAH = "In Salah"
    IN_GUEZZAM = "In Guezzam"
    TOUGGOURT = "Touggourt"
    DJANET = "Djanet"
    EL_M_GHAIR = "El M'Ghair"
    EL_MENIAA = "El Meniaa"

    @property
    def code(self) -> int:
        """
        Retourne le code numérique officiel de la wilaya.

        Returns:
            Code numérique de la wilaya (1-58)
        """
        return list(Wilaya).index(self) + 1

    def is_south(self) -> bool:
        """
        Détermine si la wilaya fait partie des régions du sud.

        Les wilayas du sud bénéficient souvent de dispositifs
        particuliers en raison de leurs spécificités géographiques
        et démographiques.

        Returns:
            True si la wilaya est dans le sud, False sinon
        """
        return self in {
            Wilaya.ADRAR,
            Wilaya.TAMANRASSET,
            Wilaya.ILLIZI,
            Wilaya.TINDOUF,
            Wilaya.IN_SALAH,
            Wilaya.IN_GUEZZAM,
        }


class Month(StrEnum):
    """
    Énumération des mois de l'année en français.

    Cette énumération fournit les noms français des mois
    avec des méthodes utilitaires pour la conversion
    numérique et le calcul des derniers jours.

    Exemples:
        >>> mois = Month.JANVIER
        >>> print(mois.value)        # "janvier"
        >>> print(mois.number)       # 1
        >>> print(mois.last_day(2024))  # 31
    """

    JANVIER = "janvier"
    FEVRIER = "février"
    MARS = "mars"
    AVRIL = "avril"
    MAI = "mai"
    JUIN = "juin"
    JUILLET = "juillet"
    AOUT = "août"
    SEPTEMBRE = "septembre"
    OCTOBRE = "octobre"
    NOVEMBRE = "novembre"
    DECEMBRE = "décembre"

    @property
    def number(self) -> int:
        """
        Retourne le numéro du mois (1-12).

        Returns:
            Numéro du mois, janvier = 1, décembre = 12
        """
        return list(Month).index(self) + 1

    @classmethod
    def from_number(cls, n: int) -> "Month":
        """
        Crée un mois à partir de son numéro.

        Args:
            n: Numéro du mois (1-12)

        Returns:
            Instance de Month correspondante

        Raises:
            IndexError: Si le numéro n'est pas valide (pas entre 1 et 12)
        """
        return list(cls)[n - 1]

    def last_day(self, year: int) -> int:
        """
        Retourne le dernier jour du mois pour une année donnée.

        Prend en compte les années bissextiles pour février.

        Args:
            year: Année pour laquelle calculer le dernier jour

        Returns:
            Numéro du dernier jour du mois (28-31)

        Exemple:
            >>> Month.FEVRIER.last_day(2024)  # 29 (année bissextile)
            >>> Month.FEVRIER.last_day(2023)  # 28 (année normale)
        """
        return monthrange(year, self.number)[1]


class Periodicity(StrEnum):
    """
    Énumération des périodicités de génération de documents.

    Définit les différentes fréquences selon lesquelles
    les documents administratifs peuvent être générés.

    Exemples:
        >>> periodicite = Periodicity.MONTHLY
        >>> print(periodicite.value)  # "monthly"
    """

    MONTHLY = "monthly"  # Documents générés mensuellement
    SEMIANNUAL = "semiannual"  # Documents générés semestriellement
    ANNUAL = "annual"  # Documents générés annuellement
