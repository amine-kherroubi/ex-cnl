from __future__ import annotations

# Standard library imports
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.core.domain.models.report_specification import ReportSpecification
from app.presentation.gui.styling.design_system import Color, Spacing, FontSize


class ReportCard(ctk.CTkFrame):
    __slots__ = (
        "_report_spec",
        "_on_generate_clicked",
        "_on_settings_clicked",
        "_generate_button",
        "_settings_button",
    )

    def __init__(
        self,
        parent: Any,
        report_spec: ReportSpecification,
        on_generate_clicked: Callable[[], None],
        on_settings_clicked: Callable[[], None],
    ) -> None:
        super().__init__(master=parent)  # type: ignore
        self._report_spec: ReportSpecification = report_spec
        self._on_generate_clicked: Callable[[], None] = on_generate_clicked
        self._on_settings_clicked: Callable[[], None] = on_settings_clicked

        self._setup_ui()

    def _setup_ui(self) -> None:
        # Configure grid
        self.grid_columnconfigure(index=0, weight=1)

        # Content frame
        content_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self, fg_color=Color.TRANSPARENT
        )
        content_frame.grid(row=0, column=0, padx=Spacing.LG, pady=Spacing.LG, sticky="ew")  # type: ignore
        content_frame.grid_columnconfigure(index=0, weight=1)

        # Report info
        info_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=content_frame, fg_color=Color.TRANSPARENT
        )
        info_frame.grid(row=0, column=0, sticky="ew")  # type: ignore
        info_frame.grid_columnconfigure(index=0, weight=1)

        # Title
        title: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text=self._report_spec.display_name,
            font=ctk.CTkFont(size=FontSize.H3, weight="bold"),
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="w")  # type: ignore

        # Details
        details: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text=f"Catégorie : {self._report_spec.category} | Fréquence : {self._report_spec.periodicity.to_french}",
            font=ctk.CTkFont(size=FontSize.CAPTION),
            text_color=Color.GRAY,
            anchor="w",
        )
        details.grid(row=1, column=0, pady=(Spacing.NONE, Spacing.SM), sticky="w")  # type: ignore

        # Description
        description: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text=self._report_spec.description,
            font=ctk.CTkFont(size=FontSize.BODY),
            anchor="w",
            wraplength=500,
            justify="left",
        )
        description.grid(row=2, column=0, pady=(Spacing.NONE, Spacing.MD), sticky="w")  # type: ignore

        # Buttons frame
        buttons_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=content_frame, fg_color=Color.TRANSPARENT
        )
        buttons_frame.grid(row=1, column=0, sticky="ew")  # type: ignore
        buttons_frame.grid_columnconfigure(index=0, weight=1)

        # Generate button - primary style
        self._generate_button: ctk.CTkButton = ctk.CTkButton(
            master=buttons_frame,
            text="Générer le rapport",
            command=self._on_generate_clicked,
            height=35,
            font=ctk.CTkFont(size=FontSize.BUTTON, weight="bold"),
        )
        self._generate_button.grid(row=0, column=0, padx=(Spacing.NONE, Spacing.SM), sticky="ew")  # type: ignore

        # Settings button - secondary style
        self._settings_button: ctk.CTkButton = ctk.CTkButton(
            master=buttons_frame,
            text="Configurer",
            command=self._on_settings_clicked,
            width=120,
            height=35,
            fg_color=Color.GRAY,
            hover_color=Color.DARKER_GRAY,
            font=ctk.CTkFont(size=FontSize.BUTTON),
        )
        self._settings_button.grid(row=0, column=1, sticky="e")  # type: ignore
