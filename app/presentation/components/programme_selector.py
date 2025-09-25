from __future__ import annotations

# Standard library imports
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.core.domain.predefined_objects.programmes import RURAL_HOUSING_PROGRAMMES
from app.presentation.components.base_component import BaseComponent
from app.presentation.styling.design_system import DesignSystem


class ProgrammeSelector(BaseComponent):
    __slots__ = (
        "_on_programme_changed",
        "_programme_selector",
        "_selected_program",
        "_programme_info_label",
        "_programme_var",
    )

    def __init__(
        self,
        parent: Any,
        on_programme_changed: Callable[[str | None], None],
    ) -> None:
        self._on_programme_changed: Callable[[str | None], None] = on_programme_changed
        self._selected_program: str | None = None

        # Initialize variable for ComboBox
        programme_names: list[str] = [
            programme.name for programme in RURAL_HOUSING_PROGRAMMES
        ]
        default_value = programme_names[0] if programme_names else ""
        self._programme_var: ctk.StringVar = ctk.StringVar(value=default_value)
        self._selected_program = default_value if programme_names else None

        super().__init__(parent, "Programme cible")

    def _setup_content(self) -> None:
        """Set up the programme selector content."""
        # Configure grid
        self._content_frame.grid_columnconfigure(index=0, weight=1)

        # Title
        title: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text=self._title,
            text_color=DesignSystem.Color.BLACK,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.H3,
                weight="bold",
            ),
            anchor="w",
        )
        title.grid(  # type: ignore
            row=0,
            column=0,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM),
            sticky="w",
        )

        # Information text
        information: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text="Sélectionnez le programme pour lequel vous souhaitez générer le rapport",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.CAPTION,
            ),
            text_color=DesignSystem.Color.GRAY,
        )
        information.grid(  # type: ignore
            row=1,
            column=0,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM),
            sticky="w",
        )

        # Programme selector - Changed from CTkOptionMenu to CTkComboBox
        programme_names: list[str] = [
            programme.name for programme in RURAL_HOUSING_PROGRAMMES
        ]

        self._programme_selector: ctk.CTkComboBox = ctk.CTkComboBox(
            master=self._content_frame,
            values=programme_names,
            variable=self._programme_var,
            command=lambda _: self._handle_programme_selection(),
            width=DesignSystem.Width.MD,  # Same as DateSelector
            height=DesignSystem.Height.SM,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL, size=DesignSystem.FontSize.BODY
            ),
            dropdown_font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL, size=DesignSystem.FontSize.BODY
            ),
            state="readonly",  # Same as DateSelector
            border_width=DesignSystem.BorderWidth.XS,  # Same as DateSelector
            corner_radius=DesignSystem.Roundness.SM,  # Same as DateSelector
        )
        self._programme_selector.grid(  # type: ignore
            row=2,
            column=0,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.MD),
            sticky="ew",
        )

        # Programme info display frame
        info_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self._content_frame,
            fg_color=DesignSystem.Color.LESS_WHITE,
            border_width=DesignSystem.BorderWidth.XS,
            border_color=DesignSystem.Color.LIGHTER_GRAY,
            corner_radius=DesignSystem.Roundness.SM,
        )
        info_frame.grid(row=3, column=0, sticky="ew")  # type: ignore
        info_frame.grid_columnconfigure(index=0, weight=1)

        # Programme info label
        self._programme_info_label: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text=self._get_programme_info_text(),
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL, size=DesignSystem.FontSize.BODY
            ),
            text_color=DesignSystem.Color.BLACK,
            justify="left",
            anchor="nw",
        )
        self._programme_info_label.grid(  # type: ignore
            row=0,
            column=0,
            padx=DesignSystem.Spacing.MD,
            pady=DesignSystem.Spacing.MD,
            sticky="w",
        )

        # Initialize with first selection
        if programme_names:
            self._on_programme_changed(self._selected_program)

    def _handle_programme_selection(self) -> None:
        """Handle programme selection change."""
        self._selected_program = self._programme_var.get()

        # Update programme info display
        self._programme_info_label.configure(text=self._get_programme_info_text())  # type: ignore

        # Notify parent of change
        self._on_programme_changed(self._selected_program)

    def _get_programme_info_text(self) -> str:
        """Get information text for the currently selected programme."""
        if not self._selected_program:
            return "Aucun programme sélectionné"

        # Find the selected programme
        for programme in RURAL_HOUSING_PROGRAMMES:
            if programme.name == self._selected_program:
                return (
                    f"Programme : {programme.name}\n"
                    f"Valeur de l'aide : {programme.aid_value:,} DA\n"
                    f"Consistance : {programme.aid_count}"
                )

        return "Information du programme non disponible"

    def get_selected_program(self) -> str | None:
        """Get the currently selected programme."""
        return self._selected_program

    def reset_to_first(self) -> None:
        """Reset selection to the first available programme."""
        programme_names: list[str] = [
            programme.name for programme in RURAL_HOUSING_PROGRAMMES
        ]

        if programme_names:
            self._programme_var.set(programme_names[0])
            self._handle_programme_selection()
