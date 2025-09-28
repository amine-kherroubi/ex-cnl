# Standard library imports
from typing import Any, Callable, Dict, List

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
        available_reports: Dict[str, Any],
        on_report_selected: Callable[[str], None],
    ) -> None:
        super().__init__(master=parent)  # type: ignore

        self._available_reports: Dict[str, Any] = available_reports
        self._on_report_selected: Callable[[str], None] = on_report_selected
        self._report_cards: List[ReportCard] = []

        self._setup_ui()

    def _setup_ui(self) -> None:

        self.configure(  # type: ignore
            fg_color=DesignSystem.Color.LEAST_WHITE.value,
            corner_radius=DesignSystem.Roundness.MD.value,
            border_color=DesignSystem.Color.LIGHTER_GRAY.value,
            border_width=DesignSystem.BorderWidth.XS.value,
        )

        self.grid_columnconfigure(index=0, weight=1)

        header_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self, fg_color=DesignSystem.Color.TRANSPARENT.value
        )
        header_frame.grid(  # type: ignore
            row=0,
            column=0,
            padx=DesignSystem.Spacing.LG.value,
            pady=(DesignSystem.Spacing.LG.value, DesignSystem.Spacing.XS.value),
            sticky="ew",
        )
        header_frame.grid_columnconfigure(index=0, weight=1)

        title: ctk.CTkLabel = ctk.CTkLabel(
            master=header_frame,
            text="Sélectionner le type de rapport",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value,
                size=DesignSystem.FontSize.H2.value,
                weight="bold",
            ),
            text_color=DesignSystem.Color.BLACK.value,
        )
        title.grid(  # type: ignore
            row=0,
            column=0,
            padx=DesignSystem.Spacing.SM.value,
            pady=(DesignSystem.Spacing.XS.value, DesignSystem.Spacing.SM.value),
            sticky="w",
        )

        description: ctk.CTkLabel = ctk.CTkLabel(
            master=header_frame,
            text="Choisissez un type de rapport à générer",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value,
                size=DesignSystem.FontSize.BODY.value,
            ),
            text_color=DesignSystem.Color.DARKER_GRAY.value,
        )
        description.grid(  # type: ignore
            row=1,
            column=0,
            padx=DesignSystem.Spacing.SM.value,
            pady=(DesignSystem.Spacing.NONE.value, DesignSystem.Spacing.XS.value),
            sticky="w",
        )

        scrollable_frame: ctk.CTkScrollableFrame = ctk.CTkScrollableFrame(
            master=self, fg_color=DesignSystem.Color.TRANSPARENT.value
        )
        scrollable_frame.grid(  # type: ignore
            row=1,
            column=0,
            padx=DesignSystem.Spacing.XS.value,
            pady=(DesignSystem.Spacing.NONE.value, DesignSystem.Spacing.LG.value),
            sticky="nsew",
        )
        scrollable_frame.grid_columnconfigure(index=0, weight=1)
        self.grid_rowconfigure(index=1, weight=1)

        for idx, (doc_name, doc_spec) in enumerate(self._available_reports.items()):
            card: ReportCard = ReportCard(
                parent=scrollable_frame,
                report_spec=doc_spec,
                on_generate_clicked=lambda name=doc_name: self._on_report_selected(
                    name
                ),
            )
            card.grid(  # type: ignore
                row=idx,
                column=0,
                padx=DesignSystem.Spacing.SM.value,
                pady=DesignSystem.Spacing.SM.value,
                sticky="ew",
            )
            self._report_cards.append(card)
