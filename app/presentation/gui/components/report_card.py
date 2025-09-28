# Standard library imports
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.core.domain.models.report_specification import ReportSpecification
from app.presentation.gui.components.base_component import BaseComponent
from app.presentation.gui.styling.design_system import DesignSystem


class ReportCard(BaseComponent):
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
        self._content_frame.grid_columnconfigure(index=0, weight=1)

        info_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self._content_frame, fg_color=DesignSystem.Color.TRANSPARENT.value
        )
        info_frame.grid(  # type: ignore
            row=0,
            column=0,
            pady=(DesignSystem.Spacing.NONE.value, DesignSystem.Spacing.MD.value),
            sticky="ew",
        )
        info_frame.grid_columnconfigure(index=0, weight=1)

        title: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text=self._report_spec.display_name,
            text_color=DesignSystem.Color.BLACK.value,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value,
                size=DesignSystem.FontSize.H3.value,
                weight="bold",
            ),
            anchor="w",
        )
        title.grid(  # type: ignore
            row=0,
            column=0,
            pady=(DesignSystem.Spacing.NONE.value, DesignSystem.Spacing.XS.value),
            sticky="w",
        )

        details: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text=f"{self._report_spec.category.value}",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value,
                size=DesignSystem.FontSize.CAPTION.value,
            ),
            text_color=DesignSystem.Color.GRAY.value,
            anchor="w",
        )
        details.grid(  # type: ignore
            row=1,
            column=0,
            pady=(DesignSystem.Spacing.NONE.value, DesignSystem.Spacing.SM.value),
            sticky="w",
        )

        description: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text=self._report_spec.description,
            text_color=DesignSystem.Color.BLACK.value,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value,
                size=DesignSystem.FontSize.BODY.value,
            ),
            anchor="w",
            wraplength=620,
            justify="left",
        )
        description.grid(row=2, column=0, sticky="w")  # type: ignore

        self._generate_button: ctk.CTkButton = ctk.CTkButton(
            master=self._content_frame,
            text="Générer le rapport",
            command=self._on_generate_clicked,
            height=DesignSystem.Height.SM.value,
            fg_color=DesignSystem.Color.PRIMARY.value,
            hover_color=DesignSystem.Color.DARKER_PRIMARY.value,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value,
                size=DesignSystem.FontSize.BUTTON.value,
            ),
            text_color=DesignSystem.Color.WHITE.value,
            corner_radius=DesignSystem.Roundness.SM.value,
        )
        self._generate_button.grid(row=1, column=0, sticky="ew")  # type: ignore
