from __future__ import annotations

# Standard library imports
from typing import Final

# Third-party imports
import pandas as pd

# Local application imports
from app.core.domain.models.programme import Programme

RURAL_HOUSING_PROGRAMMES: Final[list[Programme]] = [
    Programme(
        name="PROGRAMME 2002",
        year_start=2002,
        year_end=2002,
        display_order=1,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="COMPLEMENTAIRE 2007",
        year_start=2007,
        year_end=2007,
        display_order=2,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="PQR 2007",
        year_start=2007,
        year_end=2007,
        display_order=3,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="PROGRAMME INITIAL",
        year_start=2002,
        year_end=2002,
        display_order=4,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="COMPLEMENTAIRE 2009",
        year_start=2009,
        year_end=2009,
        display_order=5,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="PROGRAMME 2004",
        year_start=2004,
        year_end=2004,
        display_order=6,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="PROGRAMME 2003",
        year_start=2003,
        year_end=2003,
        display_order=7,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="PROGRAMME 2003 CEE",
        year_start=2003,
        year_end=2003,
        display_order=8,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="COMPLEMENTAIRE 2008",
        year_start=2008,
        year_end=2008,
        display_order=9,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="QUINQUINNAL 2010",
        year_start=2010,
        year_end=2010,
        display_order=24,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="QUINQUENNAL 2011C",
        year_start=2011,
        year_end=2011,
        display_order=28,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="QUINQUENNAL 2011",
        year_start=2011,
        year_end=2011,
        display_order=29,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="PQ2013",
        year_start=2013,
        year_end=2013,
        display_order=31,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="QUINQUENNAL 2013 C",
        year_start=2013,
        year_end=2013,
        display_order=32,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="PROGRAMME Q 2014",
        year_start=2014,
        year_end=2014,
        display_order=33,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="Programme 2015",
        year_start=2015,
        year_end=2015,
        display_order=34,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="Complémentaire 2015",
        year_start=2015,
        year_end=2015,
        display_order=37,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="Programme 2016",
        year_start=2016,
        year_end=2016,
        display_order=39,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="Programme  2018",
        year_start=2018,
        year_end=2018,
        display_order=43,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="Programme 2019",
        year_start=2019,
        year_end=2019,
        display_order=45,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="Programme 2020",
        year_start=2020,
        year_end=2020,
        display_order=47,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="Programme 2021",
        year_start=2021,
        year_end=2021,
        display_order=50,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="programme 2022",
        year_start=2022,
        year_end=2022,
        display_order=51,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="programme 2023",
        year_start=2023,
        year_end=2023,
        display_order=52,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="Programme 2024",
        year_start=2024,
        year_end=2024,
        display_order=53,
        consistance=4000,
        aid_value=700000,
    ),
    Programme(
        name="PROGRAMME 2025",
        year_start=2025,
        year_end=2025,
        display_order=55,
        consistance=4000,
        aid_value=700000,
    ),
]


def get_programmes_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "programme": programme.name,
                "year_start": programme.year_start,
                "year_end": programme.year_end,
                "display_order": programme.display_order,
                "consistance": programme.consistance,
                "aid_value": programme.aid_value,
            }
            for programme in RURAL_HOUSING_PROGRAMMES
        ]
    )
