from __future__ import annotations

# Standard library imports
from datetime import date
from calendar import monthrange
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


class Month(StrEnum):
    JANVIER = "Janvier"
    FEVRIER = "Février"
    MARS = "Mars"
    AVRIL = "Avril"
    MAI = "Mai"
    JUIN = "Juin"
    JUILLET = "Juillet"
    AOUT = "Août"
    SEPTEMBRE = "Septembre"
    OCTOBRE = "Octobre"
    NOVEMBRE = "Novembre"
    DECEMBRE = "Décembre"


class Periodicity(StrEnum):
    MONTHLY = "monthly"
    SEMIANNUAL = "semiannual"
    ANNUAL = "annual"


def month_to_numeric(month: Month) -> int:
    month_mapping: dict[Month, int] = {
        Month.JANVIER: 1,
        Month.FEVRIER: 2,
        Month.MARS: 3,
        Month.AVRIL: 4,
        Month.MAI: 5,
        Month.JUIN: 6,
        Month.JUILLET: 7,
        Month.AOUT: 8,
        Month.SEPTEMBRE: 9,
        Month.OCTOBRE: 10,
        Month.NOVEMBRE: 11,
        Month.DECEMBRE: 12,
    }
    return month_mapping[month]


def numeric_to_month(month_num: int) -> Month:
    if not 1 <= month_num <= 12:
        raise ValueError(f"Month number must be between 1 and 12, got {month_num}")

    month_mapping: dict[int, Month] = {
        1: Month.JANVIER,
        2: Month.FEVRIER,
        3: Month.MARS,
        4: Month.AVRIL,
        5: Month.MAI,
        6: Month.JUIN,
        7: Month.JUILLET,
        8: Month.AOUT,
        9: Month.SEPTEMBRE,
        10: Month.OCTOBRE,
        11: Month.NOVEMBRE,
        12: Month.DECEMBRE,
    }
    return month_mapping[month_num]


def get_last_day_of_month(year: int, month: Month) -> int:
    month_numeric: int = month_to_numeric(month)
    _, last_day = monthrange(year, month_numeric)
    return last_day


def format_french_date(date_obj: date) -> str:
    """Format date as DD/MM/YYYY (French format)."""
    return date_obj.strftime("%d/%m/%Y")


def format_period_range(start_month: Month, start_year: int, end_date: date) -> str:
    """Format a period range like 'JANVIER au 31 JANVIER 2021'."""
    end_month = numeric_to_month(end_date.month)

    if start_month == end_month and start_year == end_date.year:
        return f"{start_month.value.upper()} au {end_date.day} {end_month.value.upper()} {end_date.year}"
    else:
        return f"{start_month.value.upper()} {start_year} au {end_date.day} {end_month.value.upper()} {end_date.year}"


def format_cumulative_period(from_month: Month, from_year: int, to_date: date) -> str:
    """Format cumulative period like 'Cumul de JANVIER au 31 JANVIER 2021'."""
    period_range = format_period_range(from_month, from_year, to_date)
    return f"Cumul de {period_range}"


def is_end_of_month(date_obj: date) -> bool:
    """Check if the given date is the last day of its month."""
    _, last_day = monthrange(date_obj.year, date_obj.month)
    return date_obj.day == last_day


def is_within_period(date_obj: date, month: Month, year: int) -> bool:
    """Check if date falls within the specified month and year."""
    month_numeric = month_to_numeric(month)
    return date_obj.year == year and date_obj.month == month_numeric
