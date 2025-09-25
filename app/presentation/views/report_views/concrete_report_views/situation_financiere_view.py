from __future__ import annotations

# Standard library imports
from typing import Any, Callable

# Local application imports
from app.core.domain.models.report_specification import ReportSpecification
from app.presentation.controllers.report_controller import ReportController
from app.presentation.views.report_views.base_report_view import BaseReportView
from app.presentation.components.subprogram_selector import SubprogramSelector
from app.presentation.styling.design_system import DesignSystem


class SituationFinanciereView(BaseReportView):
    __slots__ = (
        "_subprogram_selector",
        "_selected_subprogram",
        "_selected_notification",
    )

    def __init__(
        self,
        parent: Any,
        report_spec: ReportSpecification,
        controller: ReportController,
        on_back: Callable[[], None],
    ) -> None:
        self._selected_subprogram: str | None = None
        self._selected_notification: str | None = None
        super().__init__(parent, report_spec, controller, on_back)

    def _setup_report_specific_components(self) -> None:
        self._subprogram_selector = SubprogramSelector(
            parent=self._scrollable_frame,
            on_selection_changed=self._on_selection_changed,
        )
        self._subprogram_selector.grid(  # type: ignore
            row=self._next_row,
            column=0,
            padx=DesignSystem.Spacing.SM,
            pady=DesignSystem.Spacing.SM,
            sticky="ew",
        )
        self._next_row += 1

    def _on_selection_changed(
        self, selected_subprogram: str | None, selected_notification: str | None
    ) -> None:
        self._selected_subprogram = selected_subprogram
        self._selected_notification = selected_notification
        self._update_generate_button_state()

        if hasattr(self, "_status_display"):
            if selected_subprogram and selected_notification:
                self._status_display.add_message(
                    message=f"Sélection : Sous-programme {selected_subprogram} - {selected_notification}",
                    message_type="information",
                )
            elif selected_subprogram:
                self._status_display.add_message(
                    message=f"Sous-programme sélectionné : {selected_subprogram}",
                    message_type="information",
                )

    def _can_generate(self) -> bool:
        return (
            super()._can_generate()
            and self._selected_subprogram is not None
            and self._selected_notification is not None
        )

    def _get_generation_parameters(self) -> dict[str, Any]:
        return {
            "target_subprogram": self._selected_subprogram,
            "target_notification": self._selected_notification,
        }
