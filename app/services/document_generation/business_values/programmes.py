from __future__ import annotations

# Standard library imports
from typing import Final

# Third-party imports
import pandas

# Local application imports
from app.services.document_generation.models.programe import Programme

PROGRAMMES_HABITAT_RURAL_WITH_YEARS: Final[list[Programme]] = [
    Programme(name="PROGRAMME 2002", year_start=2002, year_end=2002, display_order=1),
    Programme(
        name="COMPLEMENTAIRE 2007", year_start=2002, year_end=2002, display_order=2
    ),
    Programme(name="PQR 2007", year_start=2002, year_end=2002, display_order=3),
    Programme(
        name="PROGRAMME INITIAL", year_start=2002, year_end=2002, display_order=4
    ),
    Programme(
        name="COMPLEMENTAIRE 2009", year_start=2002, year_end=2002, display_order=5
    ),
    Programme(name="PROGRAMME 2004", year_start=2002, year_end=2002, display_order=6),
    Programme(name="PROGRAMME 2003", year_start=2002, year_end=2002, display_order=7),
    Programme(
        name="PROGRAMME 2003 CEE", year_start=2002, year_end=2002, display_order=8
    ),
    Programme(
        name="COMPLEMENTAIRE 2008", year_start=2002, year_end=2002, display_order=9
    ),
    Programme(name="PEC", year_start=2002, year_end=2002, display_order=10),
    Programme(
        name='PEC "31/12/2004"', year_start=2004, year_end=2004, display_order=11
    ),
    Programme(name="COMPL QUINQU 1", year_start=2002, year_end=2002, display_order=12),
    Programme(
        name="QUINQU 1 (2005-2009)", year_start=2005, year_end=2009, display_order=13
    ),
    Programme(
        name="QUINQU 2005-2009", year_start=2005, year_end=2009, display_order=14
    ),
    Programme(name="H PLATEAUX", year_start=2006, year_end=None, display_order=15),
    Programme(name="SUD", year_start=2007, year_end=None, display_order=16),
    Programme(name="RATTRAPAGE", year_start=2008, year_end=None, display_order=17),
    Programme(name="PRESIDENT", year_start=2008, year_end=None, display_order=18),
    Programme(name="COMPLEMENT", year_start=2008, year_end=None, display_order=19),
    Programme(
        name="COMPLEMENTAIRE 2008", year_start=2008, year_end=2008, display_order=20
    ),
    Programme(name="PROG 2008", year_start=2008, year_end=2008, display_order=21),
    Programme(name="PROG 2009", year_start=2009, year_end=2009, display_order=22),
    Programme(name="SINISTRES", year_start=2009, year_end=None, display_order=23),
    Programme(
        name="QUINQUINNAL 2010", year_start=2010, year_end=2010, display_order=24
    ),
    Programme(
        name="QUINQU 2 (2010-2014)", year_start=2010, year_end=2014, display_order=25
    ),
    Programme(
        name="QUINQU 2010-2014", year_start=2010, year_end=2014, display_order=26
    ),
    Programme(name="COMPL 2010-2014", year_start=2010, year_end=2014, display_order=27),
    Programme(
        name="QUINQUENNAL 2011C", year_start=2011, year_end=2011, display_order=28
    ),
    Programme(
        name="QUINQUENNAL 2011", year_start=2011, year_end=2011, display_order=29
    ),
    Programme(name="COMPL QUINQU 2", year_start=2011, year_end=2011, display_order=30),
    Programme(name="PQ2013", year_start=2013, year_end=2013, display_order=31),
    Programme(
        name="QUINQUENNAL 2013 C", year_start=2013, year_end=2013, display_order=32
    ),
    Programme(
        name="PROGRAMME Q 2014", year_start=2014, year_end=2014, display_order=33
    ),
    Programme(name="Programme 2015", year_start=2015, year_end=2015, display_order=34),
    Programme(
        name="QUINQU 3 (2015-2019)", year_start=2015, year_end=2019, display_order=35
    ),
    Programme(
        name="QUINQU 2015-2019", year_start=2015, year_end=2019, display_order=36
    ),
    Programme(
        name="Complémentaire 2015", year_start=2015, year_end=2015, display_order=37
    ),
    Programme(name="COMPL QUINQU 3", year_start=2015, year_end=2015, display_order=38),
    Programme(name="Programme 2016", year_start=2016, year_end=2016, display_order=39),
    Programme(name="TR 2016", year_start=2016, year_end=2016, display_order=40),
    Programme(name="QUINQU 2016", year_start=2016, year_end=None, display_order=41),
    Programme(name="INCENDIES 2017", year_start=2017, year_end=2017, display_order=42),
    Programme(name="Programme  2018", year_start=2018, year_end=2018, display_order=43),
    Programme(name="QUINQU 2018", year_start=2018, year_end=None, display_order=44),
    Programme(name="Programme 2019", year_start=2019, year_end=2019, display_order=45),
    Programme(name="QUINQU 2019", year_start=2019, year_end=None, display_order=46),
    Programme(name="Programme 2020", year_start=2020, year_end=2020, display_order=47),
    Programme(
        name="QUINQU (2020-2024)", year_start=2020, year_end=2024, display_order=48
    ),
    Programme(name="QUINQU 2020", year_start=2020, year_end=None, display_order=49),
    Programme(name="Programme 2021", year_start=2021, year_end=2021, display_order=50),
    Programme(name="programme 2022", year_start=2022, year_end=2022, display_order=51),
    Programme(name="programme 2023", year_start=2023, year_end=2023, display_order=52),
    Programme(name="Programme 2024", year_start=2024, year_end=2024, display_order=53),
    Programme(
        name="Quinquennal (2020 - 2024)",
        year_start=2020,
        year_end=2024,
        display_order=54,
    ),
    Programme(name="PROGRAMME 2025", year_start=2025, year_end=2025, display_order=55),
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
