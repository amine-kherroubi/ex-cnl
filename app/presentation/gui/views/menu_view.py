from __future__ import annotations

# Standard library imports
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.presentation.gui.components.report_card import ReportCard
from app.presentation.gui.styling.design_system import DesignSystem


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
        # Configure grid
        self.grid_columnconfigure(index=0, weight=1)

        # Header
        header_frame: ctk.CTkFrame = ctk.CTkFrame(master=self)
        header_frame.grid(row=0, column=0, padx=DesignSystem.Spacing.LG, pady=(DesignSystem.Spacing.LG, DesignSystem.Spacing.SM), sticky="ew")  # type: ignore
        header_frame.grid_columnconfigure(index=0, weight=1)

        header_label: ctk.CTkLabel = ctk.CTkLabel(
            master=header_frame,
            text="Sélectionner le type de rapport",
            font=ctk.CTkFont(size=DesignSystem.FontSize.H2, weight="bold"),
        )
        header_label.grid(row=0, column=0, padx=DesignSystem.Spacing.SM, pady=DesignSystem.Spacing.SM, sticky="w")  # type: ignore

        description_label: ctk.CTkLabel = ctk.CTkLabel(
            master=header_frame,
            text="Choisissez un type de rapport à générer ou configurez ses paramètres",
            font=ctk.CTkFont(size=DesignSystem.FontSize.LABEL),
            text_color=DesignSystem.Color.GRAY,
        )
        description_label.grid(row=1, column=0, padx=DesignSystem.Spacing.SM, pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM), sticky="w")  # type: ignore

        # Scrollable frame for report cards
        scrollable_frame: ctk.CTkScrollableFrame = ctk.CTkScrollableFrame(master=self)
        scrollable_frame.grid(row=1, column=0, padx=DesignSystem.Spacing.LG, pady=(DesignSystem.Spacing.SM, DesignSystem.Spacing.LG), sticky="nsew")  # type: ignore
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
