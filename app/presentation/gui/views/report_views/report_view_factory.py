from __future__ import annotations

# Standard library imports
from typing import Any, Callable, final

# Local application imports
from app.core.domain.models.report_specification import ReportSpecification
from app.presentation.gui.controllers.report_controller import ReportController
from app.presentation.gui.views.report_views.activite_mensuelle_report_view import (
    ActiviteMenuselleReportView,
)
from app.presentation.gui.views.report_views.base_report_view import BaseReportView
from app.presentation.gui.views.report_views.situation_financiere_report_view import (
    SituationFinanciereReportView,
)


@final
class ReportViewFactory:
    """Factory for creating appropriate report views based on report type."""

    __slots__ = ()

    @staticmethod
    def create_view(
        parent: Any,
        report_spec: ReportSpecification,
        controller: ReportController,
        on_back: Callable[[], None],
    ) -> BaseReportView:
        """Create the appropriate view for the given report specification."""

        # Map report names to their specific view classes
        view_mapping: dict[str, type[BaseReportView]] = {
            "activite_mensuelle_par_programme": ActiviteMenuselleReportView,
            "situation_financiere_des_programmes": SituationFinanciereReportView,
        }

        # Get the view class for this report type, default to DefaultReportView
        view: type[BaseReportView] | None = view_mapping.get(report_spec.name)
        if view is None:
            raise Exception()

        return view(
            parent=parent,
            report_spec=report_spec,
            controller=controller,
            on_back=on_back,
        )
