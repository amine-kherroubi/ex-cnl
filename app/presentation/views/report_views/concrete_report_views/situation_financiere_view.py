from __future__ import annotations

# Standard library imports
from typing import Any, Callable

# Local application imports
from app.core.domain.models.report_specification import ReportSpecification
from app.presentation.controllers.report_controller import ReportController
from app.presentation.views.report_views.base_report_view import BaseReportView
from app.presentation.components.programme_selector import ProgrammeSelector


class SituationFinanciereView(BaseReportView):
    """Specialized view for the Situation Financiere report with programme selection."""

    __slots__ = ("_programme_selector", "_selected_program")

    def __init__(
        self,
        parent: Any,
        report_spec: ReportSpecification,
        controller: ReportController,
        on_back: Callable[[], None],
    ) -> None:
        self._selected_program: str | None = None
        super().__init__(parent, report_spec, controller, on_back)

    def _setup_report_specific_components(self) -> None:
        """Add programme selection component specific to Situation Financiere report."""
        # Programme selector component
        self._programme_selector = ProgrammeSelector(
            parent=self._scrollable_frame,
            on_programme_changed=self._on_programme_changed,
        )
        self._programme_selector.grid(row=self._next_row, column=0, sticky="ew")  # type: ignore
        self._next_row += 1

    def _on_programme_changed(self, selected_program: str | None) -> None:
        """Handle programme selection change."""
        self._selected_program = selected_program
        self._update_generate_button_state()

        # Update status
        if hasattr(self, "_status_display") and selected_program:
            self._status_display.add_message(
                message=f"Programme sélectionné : {selected_program}",
                message_type="information",
            )

    def _can_generate(self) -> bool:
        """Override to include programme selection in validation."""
        return super()._can_generate() and self._selected_program is not None

    def _get_generation_parameters(self) -> dict[str, Any]:
        """Provide the selected programme as an additional parameter."""
        return {"target_programme": self._selected_program}
