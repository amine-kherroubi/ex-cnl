from __future__ import annotations

# Standard library imports
from calendar import monthrange
from datetime import date
from enum import StrEnum


class Wilaya(StrEnum):
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
        return list(Wilaya).index(self) + 1

    def is_south(self) -> bool:
        return self in {
            Wilaya.ADRAR,
            Wilaya.TAMANRASSET,
            Wilaya.ILLIZI,
            Wilaya.TINDOUF,
            Wilaya.IN_SALAH,
            Wilaya.IN_GUEZZAM,
        }


class Month(StrEnum):
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
        return list(Month).index(self) + 1

    @classmethod
    def from_number(cls, n: int) -> Month:
        return list(cls)[n - 1]

    @property
    def is_current(self) -> bool:
        return self.number == date.today().month

    def last_day(self, year: int) -> int:
        return monthrange(year, self.number)[1]
