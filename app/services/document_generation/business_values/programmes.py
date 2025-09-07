from __future__ import annotations

# Standard library imports
from typing import Final

# Third-party imports
import pandas

# Local application imports
from app.services.document_generation.models.programe import Programme

PROGRAMMES_HABITAT_RURAL_WITH_YEARS: Final[list[Programme]] = [
    Programme(name='PEC "31/12/2004"', year_start=2004, year_end=2004, display_order=1),
    Programme(name="QUINQU 2005-2009", year_start=2005, year_end=2009, display_order=2),
    Programme(name="H PLATEAUX", year_start=2006, year_end=None, display_order=3),
    Programme(name="SUD", year_start=2007, year_end=None, display_order=4),
    Programme(name="RATTRAPAGE", year_start=2008, year_end=None, display_order=5),
    Programme(name="PRESIDENT", year_start=2008, year_end=None, display_order=6),
    Programme(name="COMPLEMENT", year_start=2008, year_end=None, display_order=7),
    Programme(name="PROG 2008", year_start=2008, year_end=2008, display_order=8),
    Programme(name="PROG 2009", year_start=2009, year_end=2009, display_order=9),
    Programme(name="SINISTRES", year_start=2009, year_end=None, display_order=10),
    Programme(
        name="QUINQU 2010-2014", year_start=2010, year_end=2014, display_order=11
    ),
    Programme(name="COMPL 2010-2014", year_start=2010, year_end=2014, display_order=12),
    Programme(
        name="QUINQU 2015-2019", year_start=2015, year_end=2019, display_order=13
    ),
    Programme(name="TR 2016", year_start=2016, year_end=2016, display_order=14),
    Programme(name="INCENDIES 2017", year_start=2017, year_end=2017, display_order=15),
    Programme(name="QUINQU 2016", year_start=2016, year_end=None, display_order=16),
    Programme(name="QUINQU 2018", year_start=2018, year_end=None, display_order=17),
    Programme(name="QUINQU 2019", year_start=2019, year_end=None, display_order=18),
    Programme(name="QUINQU 2020", year_start=2020, year_end=None, display_order=19),
]


def get_programmes_dataframe() -> pandas.DataFrame:
    return pandas.DataFrame(
        [
            {
                "programme": prog.name,
                "year_start": prog.year_start,
                "year_end": prog.year_end,
                "display_order": prog.display_order,
            }
            for prog in PROGRAMMES_HABITAT_RURAL_WITH_YEARS
        ]
    )
