from __future__ import annotations

# Standard library imports
from typing import Final

# Third-party imports
import pandas as pd
import pytest

NUMBER_OF_DAIRAS: Final[int] = 21
NUMBER_OF_COMMUNES: Final[int] = 67

DAIRAS_TIZI_OUZOU: Final[set[str]] = {
    "AIN EL HAMMAM",
    "AZZAZGA",
    "AZZEFOUN",
    "BENI DOUALA",
    "BENNI YENNI",
    "BOGHNI",
    "BOUZEGUENE",
    "DRAA BEN KHEDDA",
    "DRAA EL MIZAN",
    "IFERHOUNENE",
    "LARBA NATH IRATEN",
    "MAATKA",
    "MAKOUDA",
    "MEKLA",
    "OUACIF",
    "OUADHIA",
    "OUAGUENOUN",
    "TIGZIRT",
    "TIZI GHENIF",
    "TIZI OUZOU",
    "TIZI RACHED",
}

COMMUNES_TIZI_OUZOU: Final[set[str]] = {
    "01_TIZI_OUZOU",
    "02_AIN EL HAMMAM",
    "03_AKBIL",
    "04_FREHA",
    "05_SOUAMAA",
    "06_MECHTRASS",
    "07_IRDJEN",
    "08_TIMIZART",
    "09_MAKOUDA",
    "10_DRAA EL MIZAN",
    "11_TIZI GHENIF",
    "12_BOUNOUH",
    "13_AIT CHAFFAA",
    "14_FRIKAT",
    "15_BENI AISSI",
    "16_BENI ZMENZER",
    "17_IFERHOUNENE",
    "18_AZAZGA",
    "19_ILOULA OUMALOU",
    "20_YAKOUREN",
    "21_LARBA NAIT IRATHEN",
    "22_TIZI_RACHED",
    "23_ZEKRI",
    "24_OUAGUENOUN",
    "25_AIN ZAOUIA",
    "26_M'KIRA",
    "27_AIT YAHIA",
    "28_AIT MAHMOUD",
    "29_MAATKA",
    "30_AIT BOUMEHDI",
    "31_ABI YOUCEF",
    "32_BENI DOUALA",
    "33_ILLILTEN",
    "34_BOUZGUEN",
    "35_AIT AGGOUACHA",
    "36_OUADHIA",
    "37_AZZEFOUN",
    "38_TIGZIRT",
    "39_DJEBEL AISSA MIMOUN",
    "40_BOGHNI",
    "41_IFIGHA",
    "42_AIT OUMALOU",
    "43_TIRMIRTINE",
    "44_AKERROU",
    "45_YATAFENE",
    "46_BENI ZIKI",
    "47_DRAA BEN KHEDA",
    "48_OUACIF",
    "49_IDJEUR",
    "50_MEKLA",
    "51_TIZI N'THLATA",
    "52_BENI YENNI",
    "53_AGHRIB",
    "54_IFLISSEN",
    "55_BOUDJIMA",
    "56_AIT YAHIA MOU",
    "57_SOUK EL TENINE",
    "58_AIT KHELILI",
    "59_SIDI NAAMANE",
    "60_IBOUDRAREN",
    "61_AGHNI GOUGHRAN",
    "62_MIZRANA",
    "63_IMSOUHAL",
    "64_TADMAIT",
    "65_AIT BOUADDOU",
    "66_ASSI YOUCEF",
    "67_AIT TOUDERT",
}

# Official mapping based on Wikipedia data
DAIRA_COMMUNE_MAPPING: Final[dict[str, list[str]]] = {
    "AIN EL HAMMAM": [
        "31_ABI YOUCEF",
        "02_AIN EL HAMMAM",
        "27_AIT YAHIA",
        "03_AKBIL",
    ],
    "AZZAZGA": [
        "18_AZAZGA",
        "04_FREHA",
        "41_IFIGHA",
        "20_YAKOUREN",
        "23_ZEKRI",
    ],
    "AZZEFOUN": [
        "53_AGHRIB",
        "13_AIT CHAFFAA",
        "44_AKERROU",
        "37_AZZEFOUN",
    ],
    "BENI DOUALA": [
        "28_AIT MAHMOUD",
        "15_BENI AISSI",
        "32_BENI DOUALA",
        "16_BENI ZMENZER",
    ],
    "BENNI YENNI": [
        "52_BENI YENNI",
        "60_IBOUDRAREN",
        "45_YATAFENE",
    ],
    "BOGHNI": [
        "66_ASSI YOUCEF",
        "40_BOGHNI",
        "12_BOUNOUH",
        "06_MECHTRASS",
    ],
    "BOUZEGUENE": [
        "46_BENI ZIKI",
        "34_BOUZGUEN",
        "49_IDJEUR",
        "19_ILOULA OUMALOU",
    ],
    "DRAA BEN KHEDDA": [
        "47_DRAA BEN KHEDA",
        "59_SIDI NAAMANE",
        "64_TADMAIT",
        "43_TIRMIRTINE",
    ],
    "DRAA EL MIZAN": [
        "25_AIN ZAOUIA",
        "56_AIT YAHIA MOU",
        "10_DRAA EL MIZAN",
        "14_FRIKAT",
    ],
    "IFERHOUNENE": [
        "17_IFERHOUNENE",
        "33_ILLILTEN",
        "63_IMSOUHAL",
    ],
    "LARBA NATH IRATEN": [
        "35_AIT AGGOUACHA",
        "07_IRDJEN",
        "21_LARBA NAIT IRATHEN",
    ],
    "MAATKA": [
        "29_MAATKA",
        "57_SOUK EL TENINE",
    ],
    "MAKOUDA": [
        "55_BOUDJIMA",
        "09_MAKOUDA",
    ],
    "MEKLA": [
        "58_AIT KHELILI",
        "50_MEKLA",
        "05_SOUAMAA",
    ],
    "OUACIF": [
        "30_AIT BOUMEHDI",
        "67_AIT TOUDERT",
        "48_OUACIF",
    ],
    "OUADHIA": [
        "61_AGHNI GOUGHRAN",
        "65_AIT BOUADDOU",
        "36_OUADHIA",
        "51_TIZI N'THLATA",
    ],
    "OUAGUENOUN": [
        "39_DJEBEL AISSA MIMOUN",
        "24_OUAGUENOUN",
        "08_TIMIZART",
    ],
    "TIGZIRT": [
        "54_IFLISSEN",
        "62_MIZRANA",
        "38_TIGZIRT",
    ],
    "TIZI GHENIF": [
        "26_M'KIRA",
        "11_TIZI GHENIF",
    ],
    "TIZI OUZOU": [
        "01_TIZI_OUZOU",
    ],
    "TIZI RACHED": [
        "42_AIT OUMALOU",
        "22_TIZI_RACHED",
    ],
}


def create_daira_commune_dataframe() -> pd.DataFrame:
    """Create a pandas DataFrame mapping each commune to its corresponding daira, sorted alphabetically."""
    data: list[dict[str, str]] = []
    for daira, communes in DAIRA_COMMUNE_MAPPING.items():
        for commune in communes:
            data.append({"Daira": daira, "Commune": commune})

    df: pd.DataFrame = pd.DataFrame(data)
    return df.sort_values(["Daira", "Commune"]).reset_index(drop=True)


# Unit tests


def test_daira_count():
    assert (
        len(DAIRA_COMMUNE_MAPPING) == NUMBER_OF_DAIRAS
    ), f"Expected 21 dairas, got {len(DAIRA_COMMUNE_MAPPING)}"


def test_commune_count():
    mapped_communes: set[str] = set()
    for communes in DAIRA_COMMUNE_MAPPING.values():
        mapped_communes.update(communes)

    assert (
        len(mapped_communes) == NUMBER_OF_COMMUNES
    ), f"Expected 67 communes, got {len(mapped_communes)}"


def test_all_communes_mapped():
    mapped_communes: set[str] = set()
    for communes in DAIRA_COMMUNE_MAPPING.values():
        mapped_communes.update(communes)

    assert (
        mapped_communes == COMMUNES_TIZI_OUZOU
    ), f"Missing communes: {COMMUNES_TIZI_OUZOU - mapped_communes}, Extra communes: {mapped_communes - COMMUNES_TIZI_OUZOU}"


def test_no_duplicate_communes():
    all_communes: list[str] = []
    for communes in DAIRA_COMMUNE_MAPPING.values():
        all_communes.extend(communes)

    duplicates: list[str] = [
        commune for commune in set(all_communes) if all_communes.count(commune) > 1
    ]
    assert not duplicates, f"Duplicate communes found: {duplicates}"


def test_all_mapped_dairas_exist():
    mapped_dairas: set[str] = set(DAIRA_COMMUNE_MAPPING.keys())
    assert (
        mapped_dairas <= DAIRAS_TIZI_OUZOU
    ), f"Invalid dairas in mapping: {mapped_dairas - DAIRAS_TIZI_OUZOU}"


def test_dataframe_structure():
    df: pd.DataFrame = create_daira_commune_dataframe()

    assert list(df.columns) == [
        "Daira",
        "Commune",
    ], "DataFrame should have columns ['Daira', 'Commune']"
    assert (
        len(df) == NUMBER_OF_COMMUNES
    ), f"DataFrame should have 67 rows, got {len(df)}"
    assert df["Daira"].notna().all(), "No null values allowed in Daira column"
    assert df["Commune"].notna().all(), "No null values allowed in Commune column"

    is_sorted: bool = df.equals(
        df.sort_values(["Daira", "Commune"]).reset_index(drop=True)
    )
    assert is_sorted, "DataFrame should be sorted by Daira then Commune"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
