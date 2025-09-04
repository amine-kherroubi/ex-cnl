from __future__ import annotations
from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class DatabaseConfig(object):
    connection_timeout: Final[int] = 30
    query_timeout: Final[int] = 300
    enable_debug: Final[bool] = True


@dataclass(frozen=True)
class ApplicationConfig(object):
    input_file: Final[str] = (
        "Liste_OVs_Agence_TIZIOUZOU_17.09.2024_7284743114531606447.xlsx"
    )
    output_file: Final[str] = "result.xlsx"
    database: Final[DatabaseConfig] = DatabaseConfig()
