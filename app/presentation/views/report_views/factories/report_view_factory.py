from __future__ import annotations

# Standard library imports
from typing import Any, Callable, final

# Local application imports
from app.core.domain.models.report_specification import ReportSpecification
from app.core.facade import CoreFacade
from app.presentation.views.report_views.concrete_report_views.activite_mensuelle_view import (
    ActiviteMenuselleView,
)
from app.presentation.views.report_views.base_report_view import BaseReportView
from app.presentation.views.report_views.concrete_report_views.situation_financiere_view import (
    SituationFinanciereView,
)


@final
class ReportViewFactory(object):

    __slots__ = ()

    @staticmethod
    def create_view(
        parent: Any,
        report_spec: ReportSpecification,
        core_facade: CoreFacade,
        on_back: Callable[[], None],
    ) -> BaseReportView:

        view_mapping: dict[str, type[BaseReportView]] = {
            "activite_mensuelle": ActiviteMenuselleView,
            "situation_financiere": SituationFinanciereView,
        }

        view: type[BaseReportView] | None = view_mapping.get(report_spec.name)
        if view is None:
            raise Exception()

        return view(
            parent=parent,
            report_spec=report_spec,
            core_facade=core_facade,
            on_back=on_back,
        )
