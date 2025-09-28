# Standard library imports
from typing import Dict, Type

# Local application imports
from app.presentation.gui.views.report_views.base_report_view import BaseReportView
from .activite_mensuelle import ActiviteMenuselleView
from .situation_financiere import SituationFinanciereView
from .situation_par_sous_programme import SituationParSousProgrammeView

__all__ = [
    "ActiviteMenuselleView",
    "SituationFinanciereView",
    "SituationParSousProgrammeView",
    "views",
]

views: Dict[str, Type[BaseReportView]] = {
    "activite_mensuelle": ActiviteMenuselleView,
    "situation_financiere": SituationFinanciereView,
    "situation_par_sous_programme": SituationParSousProgrammeView,
}
