from __future__ import annotations

# Standard library imports
from typing import Any, Callable

# Local application imports
from app.core.domain.models.notification import Notification
from app.core.domain.models.report_specification import ReportSpecification
from app.core.domain.models.subprogram import Subprogram
from app.presentation.views.report_views.base_report_view import BaseReportView
from app.presentation.components.subprogram_selector import SubprogramSelector
from app.presentation.styling.design_system import DesignSystem
from app.core.facade import CoreFacade


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
        core_facade: CoreFacade,
        on_back: Callable[[], None],
    ) -> None:
        self._selected_subprogram: Subprogram | None = None
        self._selected_notification: Notification | None = None
        super().__init__(parent, report_spec, core_facade, on_back)

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
        self,
        selected_subprogram: Subprogram,
        selected_notification: Notification,
    ) -> None:
        self._selected_subprogram = selected_subprogram
        self._selected_notification = selected_notification
        self._update_generate_button_state()

        if hasattr(self, "_status_display"):
            self._status_display.add_message(
                message=f"Sélection : Sous-programme {selected_subprogram.name} - Notification {selected_notification.name}",
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
