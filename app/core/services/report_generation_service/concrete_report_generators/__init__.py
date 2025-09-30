# Standard library imports
from typing import Dict, Type

# Local application imports
from app.core.services.report_generation_service.base_report_generator import (
    BaseGenerator,
)
from .activite_mensuelle import ActiviteMensuelleGenerator
from .situation_financiere import SituationFinanciereGenerator
from .situation_par_sous_programme import SituationParSousProgrammeGenerator

__all__ = [
    "ActiviteMensuelleGenerator",
    "SituationFinanciereGenerator",
    "SituationParSousProgrammeGenerator",
    "generators",
]

generators: Dict[str, Type[BaseGenerator]] = {
    "activite_mensuelle": ActiviteMensuelleGenerator,
    "situation_financiere": SituationFinanciereGenerator,
    "situation_par_sous_programme": SituationParSousProgrammeGenerator,
}
