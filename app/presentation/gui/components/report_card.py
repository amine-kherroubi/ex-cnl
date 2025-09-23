from __future__ import annotations

# Standard library imports
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.core.domain.models.report_specification import ReportSpecification
from app.presentation.gui.components.base_component import BaseComponent
from app.presentation.gui.styling.design_system import DesignSystem


class ReportCard(BaseComponent):
    """Component displaying a report card with generation option."""

    __slots__ = (
        "_report_spec",
        "_on_generate_clicked",
        "_generate_button",
    )

    def __init__(
        self,
        parent: Any,
        report_spec: ReportSpecification,
        on_generate_clicked: Callable[[], None],
    ) -> None:
        self._report_spec: ReportSpecification = report_spec
        self._on_generate_clicked: Callable[[], None] = on_generate_clicked

        super().__init__(parent, report_spec.display_name)

    def _setup_content(self) -> None:
        """Set up the report card content."""
        # Configure grid
        self._content_frame.grid_columnconfigure(index=0, weight=1)

        # Report info frame
        info_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self._content_frame, fg_color=DesignSystem.Color.TRANSPARENT
        )
        info_frame.grid(  # type: ignore
            row=0,
            column=0,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.MD),
            sticky="ew",
        )
        info_frame.grid_columnconfigure(index=0, weight=1)

        # Title
        title: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text=self._report_spec.display_name,
            text_color=DesignSystem.Color.BLACK,
            font=ctk.CTkFont(size=DesignSystem.FontSize.H3, weight="bold"),
            anchor="w",
        )
        title.grid(  # type: ignore
            row=0,
            column=0,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.XS),
            sticky="w",
        )

        # Category details
        details: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text=f"Catégorie : {self._report_spec.category}",
            font=ctk.CTkFont(size=DesignSystem.FontSize.CAPTION),
            text_color=DesignSystem.Color.DARKER_GRAY,
            anchor="w",
        )
        details.grid(  # type: ignore
            row=1,
            column=0,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM),
            sticky="w",
        )

        # Description
        description: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text=self._report_spec.description,
            text_color=DesignSystem.Color.BLACK,
            font=ctk.CTkFont(size=DesignSystem.FontSize.BODY),
            anchor="w",
            wraplength=700,
            justify="left",
        )
        description.grid(row=2, column=0, sticky="w")  # type: ignore

        # Generate button
        self._generate_button: ctk.CTkButton = ctk.CTkButton(
            master=self._content_frame,
            text="Générer le rapport",
            command=self._on_generate_clicked,
            height=DesignSystem.Height.SM,
            fg_color=DesignSystem.Color.PRIMARY,
            hover_color=DesignSystem.Color.DARKER_PRIMARY,
            font=ctk.CTkFont(size=DesignSystem.FontSize.BUTTON, weight="bold"),
            text_color=DesignSystem.Color.WHITE,
            corner_radius=DesignSystem.Roundness.SM,
        )
        self._generate_button.grid(row=1, column=0, sticky="ew")  # type: ignore
