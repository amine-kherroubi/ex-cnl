from __future__ import annotations

# Standard library imports
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.presentation.components.report_card import ReportCard
from app.presentation.styling.design_system import DesignSystem


class MenuView(ctk.CTkFrame):
    __slots__ = (
        "_available_reports",
        "_on_report_selected",
        "_report_cards",
    )

    def __init__(
        self,
        parent: Any,
        available_reports: dict[str, Any],
        on_report_selected: Callable[[str], None],
    ) -> None:
        super().__init__(master=parent)  # type: ignore

        self._available_reports: dict[str, Any] = available_reports
        self._on_report_selected: Callable[[str], None] = on_report_selected
        self._report_cards: list[ReportCard] = []

        self._setup_ui()

    def _setup_ui(self) -> None:
        # Self configuration
        self.configure(  # type: ignore
            fg_color=DesignSystem.Color.LEAST_WHITE,
            corner_radius=DesignSystem.Roundness.MD,
            border_color=DesignSystem.Color.LIGHTER_GRAY,
            border_width=DesignSystem.BorderWidth.XS,
        )

        # Configure grid
        self.grid_columnconfigure(index=0, weight=1)

        # Header
        header_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self, fg_color=DesignSystem.Color.TRANSPARENT
        )
        header_frame.grid(row=0, column=0, padx=DesignSystem.Spacing.LG, pady=(DesignSystem.Spacing.LG, DesignSystem.Spacing.XS), sticky="ew")  # type: ignore
        header_frame.grid_columnconfigure(index=0, weight=1)

        title: ctk.CTkLabel = ctk.CTkLabel(
            master=header_frame,
            text="Sélectionner le type de rapport",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.H2,
                weight="bold",
            ),
            text_color=DesignSystem.Color.BLACK,
        )
        title.grid(row=0, column=0, padx=DesignSystem.Spacing.SM, pady=(DesignSystem.Spacing.XS, DesignSystem.Spacing.SM), sticky="w")  # type: ignore

        description: ctk.CTkLabel = ctk.CTkLabel(
            master=header_frame,
            text="Choisissez un type de rapport à générer",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL, size=DesignSystem.FontSize.BODY
            ),
            text_color=DesignSystem.Color.DARKER_GRAY,
        )
        description.grid(row=1, column=0, padx=DesignSystem.Spacing.SM, pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.XS), sticky="w")  # type: ignore

        # Scrollable frame for report cards
        scrollable_frame: ctk.CTkScrollableFrame = ctk.CTkScrollableFrame(
            master=self, fg_color=DesignSystem.Color.TRANSPARENT
        )
        scrollable_frame.grid(row=1, column=0, padx=DesignSystem.Spacing.XS, pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.LG), sticky="nsew")  # type: ignore
        scrollable_frame.grid_columnconfigure(index=0, weight=1)
        self.grid_rowconfigure(index=1, weight=1)

        # Create report cards
        for idx, (doc_name, doc_spec) in enumerate(self._available_reports.items()):
            card: ReportCard = ReportCard(
                parent=scrollable_frame,
                report_spec=doc_spec,
                on_generate_clicked=lambda name=doc_name: self._on_report_selected(
                    name
                ),
            )
            card.grid(row=idx, column=0, padx=DesignSystem.Spacing.SM, pady=DesignSystem.Spacing.SM, sticky="ew")  # type: ignore
            self._report_cards.append(card)
