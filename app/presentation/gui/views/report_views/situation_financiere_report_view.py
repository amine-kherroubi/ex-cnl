from __future__ import annotations

# Standard library imports
from typing import Any

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.core.domain.predefined_objects.programmes import RURAL_HOUSING_PROGRAMMES
from app.presentation.gui.views.report_views.base_report_view import BaseReportView
from app.presentation.gui.styling.design_system import DesignSystem


class SituationFinanciereReportView(BaseReportView):
    """Specialized view for the Situation Financiere report with program selection."""

    __slots__ = ("_program_selector", "_selected_program", "_program_info_label")

    def __init__(
        self, parent: Any, report_spec: Any, controller: Any, on_back: Any
    ) -> None:
        self._selected_program: str | None = None
        super().__init__(parent, report_spec, controller, on_back)

    def _setup_report_specific_components(self) -> None:
        """Add program selection component specific to Situation Financiere report."""
        # Program selection frame
        program_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self._scrollable_frame,
            fg_color=DesignSystem.Color.TRANSPARENT,
        )
        program_frame.grid(row=self._next_row, column=0, padx=DesignSystem.Spacing.LG, pady=(DesignSystem.Spacing.SM, DesignSystem.Spacing.SM), sticky="ew")  # type: ignore
        program_frame.grid_columnconfigure(index=0, weight=1)
        self._next_row += 1

        # Program selection title
        program_title: ctk.CTkLabel = ctk.CTkLabel(
            master=program_frame,
            text="Programme cible",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily,
                size=DesignSystem.FontSize.H3,
                weight="bold",
            ),
        )
        program_title.grid(row=0, column=0, pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM), sticky="w")  # type: ignore

        # Program selector
        program_names: list[str] = [
            program.name for program in RURAL_HOUSING_PROGRAMMES
        ]

        self._program_selector = ctk.CTkOptionMenu(
            master=program_frame,
            values=program_names,
            command=self._on_program_changed,
            height=36,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily, size=DesignSystem.FontSize.BODY
            ),
        )
        self._program_selector.grid(row=1, column=0, sticky="ew")  # type: ignore

        # Set default selection if programs are available
        if program_names:
            self._program_selector.set(program_names[0])
            self._selected_program = program_names[0]

        # Program info display
        self._create_program_info_section(program_frame)

    def _create_program_info_section(self, parent: ctk.CTkFrame) -> None:
        """Create a section to display information about the selected program."""
        info_frame: ctk.CTkFrame = ctk.CTkFrame(master=parent)
        info_frame.grid(row=2, column=0, pady=(DesignSystem.Spacing.SM, DesignSystem.Spacing.NONE), sticky="ew")  # type: ignore

        self._program_info_label: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text=self._get_program_info_text(),
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily, size=DesignSystem.FontSize.BODY
            ),
            justify="left",
            anchor="w",
        )
        self._program_info_label.grid(row=0, column=0, padx=DesignSystem.Spacing.MD, pady=DesignSystem.Spacing.MD, sticky="w")  # type: ignore

    def _get_program_info_text(self) -> str:
        """Get information text for the currently selected program."""
        if not self._selected_program:
            return "Aucun programme sélectionné"

        # Find the selected program
        for program in RURAL_HOUSING_PROGRAMMES:
            if program.name == self._selected_program:
                return (
                    f"Programme : {program.name}\n"
                    f"Valeur de l'aide : {program.aid_value:,} DA\n"
                    f"Consistance : {program.consistance}"
                )

        return "Information du programme non disponible"

    def _on_program_changed(self, selected_program: str) -> None:
        """Handle program selection change."""
        self._selected_program = selected_program
        self._update_generate_button_state()

        # Update program info display
        if hasattr(self, "_program_info_label"):
            self._program_info_label.configure(text=self._get_program_info_text())  # type: ignore

        # Update status
        if hasattr(self, "_status_display"):
            self._status_display.add_message(
                message=f"Programme sélectionné : {selected_program}",
                message_type="information",
            )

    def _can_generate(self) -> bool:
        """Override to include program selection in validation."""
        return super()._can_generate() and self._selected_program is not None

    def _get_generation_parameters(self) -> dict[str, Any]:
        """Provide the selected program as an additional parameter."""
        return {"target_programme": self._selected_program}
