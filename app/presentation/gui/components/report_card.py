from __future__ import annotations

# Standard library imports
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.core.domain.models.report_specification import ReportSpecification
from app.presentation.gui.styling.design_system import DesignSystem


class ReportCard(ctk.CTkFrame):
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
        super().__init__(master=parent)  # type: ignore
        self._report_spec: ReportSpecification = report_spec
        self._on_generate_clicked: Callable[[], None] = on_generate_clicked

        self._setup_ui()

    def _setup_ui(self) -> None:
        # Self configuration
        self.configure(  # type: ignore
            fg_color=DesignSystem.Color.WHITE,
            corner_radius=DesignSystem.Roundness.NORMAL,
        )

        # Configure grid
        self.grid_columnconfigure(index=0, weight=1)

        # Content frame
        content_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self, fg_color=DesignSystem.Color.TRANSPARENT
        )
        content_frame.grid(row=0, column=0, padx=DesignSystem.Spacing.LG, pady=DesignSystem.Spacing.LG, sticky="ew")  # type: ignore
        content_frame.grid_columnconfigure(index=0, weight=1)

        # Report info
        info_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=content_frame, fg_color=DesignSystem.Color.TRANSPARENT
        )
        info_frame.grid(row=0, column=0, sticky="ew")  # type: ignore
        info_frame.grid_columnconfigure(index=0, weight=1)

        # Title
        title: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text=self._report_spec.display_name,
            text_color=DesignSystem.Color.BLACK,
            font=ctk.CTkFont(size=DesignSystem.FontSize.H3, weight="bold"),
            anchor="w",
        )
        title.grid(row=0, column=0, pady=DesignSystem.Spacing.NONE, sticky="w")  # type: ignore

        # Details
        details: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text=f"Catégorie : {self._report_spec.category}",
            font=ctk.CTkFont(size=DesignSystem.FontSize.CAPTION),
            text_color=DesignSystem.Color.DARKER_GRAY,
            anchor="w",
        )
        details.grid(row=1, column=0, pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.MD), sticky="w")  # type: ignore

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
        description.grid(row=2, column=0, pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.MD), sticky="w")  # type: ignore

        # Generate button - primary style
        self._generate_button: ctk.CTkButton = ctk.CTkButton(
            master=content_frame,
            text="Générer le rapport",
            command=self._on_generate_clicked,
            height=35,
            fg_color=DesignSystem.Color.PRIMARY,
            font=ctk.CTkFont(size=DesignSystem.FontSize.BUTTON, weight="bold"),
            text_color=DesignSystem.Color.WHITE,
            hover_color=DesignSystem.Color.DARKER_PRIMARY,
            corner_radius=DesignSystem.Roundness.SMALL,
        )
        self._generate_button.grid(row=3, column=0, sticky="ew")  # type: ignore
