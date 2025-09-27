

# Standard library imports
from datetime import date
from typing import Any, Callable, Optional, List

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.core.domain.enums.space_time import Month
from app.presentation.gui.components.base_component import BaseComponent
from app.presentation.gui.styling.design_system import DesignSystem


class DateSelector(BaseComponent):

    __slots__ = (
        "_on_date_changed",
        "_month_var",
        "_year_var",
        "_month_dropdown",
        "_year_dropdown",
        "_current_month",
        "_current_year",
    )

    def __init__(
        self,
        parent: Any,
        on_date_changed: Callable[[Optional[Month], Optional[int]], None],
    ) -> None:
        self._on_date_changed: Callable[[Optional[Month], Optional[int]], None] = (
            on_date_changed
        )

        today: date = date.today()
        self._current_month: Month = Month.from_number(today.month)
        self._current_year: int = today.year

        self._month_var: ctk.StringVar = ctk.StringVar(
            value=self._current_month.value.capitalize()
        )
        self._year_var: ctk.StringVar = ctk.StringVar(value=str(self._current_year))

        super().__init__(parent, "Période du rapport")

    def _setup_content(self) -> None:
        self._content_frame.grid_columnconfigure(index=1, weight=1)
        self._content_frame.grid_columnconfigure(index=3, weight=1)

        title: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text=self._title,
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
            columnspan=4,
            pady=(DesignSystem.Spacing.NONE.value, DesignSystem.Spacing.SM.value),
            sticky="w",
        )

        information: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text="Sélectionnez la période pour laquelle vous souhaitez générer le rapport",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value,
                size=DesignSystem.FontSize.CAPTION.value,
            ),
            text_color=DesignSystem.Color.GRAY.value,
        )
        information.grid(  # type: ignore
            row=1,
            columnspan=4,
            column=0,
            pady=(DesignSystem.Spacing.NONE.value, DesignSystem.Spacing.SM.value),
            sticky="w",
        )

        year_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text="Année :",
            text_color=DesignSystem.Color.BLACK.value,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value, size=DesignSystem.FontSize.BODY.value,
            ),
        )
        year_label.grid(  # type: ignore
            row=2,
            column=0,
            padx=(DesignSystem.Spacing.NONE.value, DesignSystem.Spacing.SM.value),
            sticky="w",
        )

        year_values: list[str] = [
            str(year) for year in range(self._current_year, 1999, -1)
        ]
        self._year_dropdown: ctk.CTkComboBox = ctk.CTkComboBox(
            master=self._content_frame,
            values=year_values,
            variable=self._year_var,
            command=lambda _: self._on_year_changed(),
            width=DesignSystem.Width.MD.value,
            height=DesignSystem.Height.SM.value,
            text_color=DesignSystem.Color.BLACK.value,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value, size=DesignSystem.FontSize.BODY.value
            ),
            dropdown_font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value, size=DesignSystem.FontSize.BODY.value
            ),
            state="readonly",
            border_width=DesignSystem.BorderWidth.XS.value,
            corner_radius=DesignSystem.Roundness.XS.value,
            fg_color=DesignSystem.Color.LESS_WHITE.value,
            border_color=DesignSystem.Color.LIGHTER_GRAY.value,
            button_color=DesignSystem.Color.LIGHTER_GRAY.value,
            button_hover_color=DesignSystem.Color.GRAY.value,
            dropdown_fg_color=DesignSystem.Color.LESS_WHITE.value,
            dropdown_text_color=DesignSystem.Color.BLACK.value,
            dropdown_hover_color=DesignSystem.Color.LIGHTER_GRAY.value,
        )
        self._year_dropdown.grid(  # type: ignore
            row=2,
            column=1,
            padx=(DesignSystem.Spacing.NONE.value, DesignSystem.Spacing.MD.value),
            sticky="ew",
        )

        month_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text="Mois :",
            text_color=DesignSystem.Color.BLACK.value,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value, size=DesignSystem.FontSize.BODY.value,
            ),
        )
        month_label.grid(  # type: ignore
            row=2,
            column=2,
            padx=(DesignSystem.Spacing.NONE.value, DesignSystem.Spacing.SM.value),
            sticky="w",
        )

        # Initialize month dropdown with current year's available months
        self._month_dropdown: ctk.CTkComboBox = ctk.CTkComboBox(
            master=self._content_frame,
            values=self._get_available_months(),
            variable=self._month_var,
            command=lambda _: self._on_month_changed(),
            width=DesignSystem.Width.MD.value,
            height=DesignSystem.Height.SM.value,
            text_color=DesignSystem.Color.BLACK.value,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value, size=DesignSystem.FontSize.BODY.value
            ),
            dropdown_font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value, size=DesignSystem.FontSize.BODY.value
            ),
            state="readonly",
            border_width=DesignSystem.BorderWidth.XS.value,
            corner_radius=DesignSystem.Roundness.SM.value,
            fg_color=DesignSystem.Color.LESS_WHITE.value,
            border_color=DesignSystem.Color.LIGHTER_GRAY.value,
            button_color=DesignSystem.Color.LIGHTER_GRAY.value,
            button_hover_color=DesignSystem.Color.GRAY.value,
            dropdown_fg_color=DesignSystem.Color.LESS_WHITE.value,
            dropdown_text_color=DesignSystem.Color.BLACK.value,
            dropdown_hover_color=DesignSystem.Color.LIGHTER_GRAY.value,
        )
        self._month_dropdown.grid(  # type: ignore
            row=2,
            column=3,
            sticky="ew",
        )

    def _get_available_months(self) -> List[str]:
        """Get available months based on selected year."""
        try:
            selected_year = int(self._year_var.get())
        except ValueError:
            selected_year = self._current_year

        if selected_year == self._current_year:
            # For current year, only show months up to current month
            available_months = []
            for month in Month:
                if month.number <= self._current_month.number:
                    available_months.append(month.value.capitalize())  # type: ignore
            return available_months  # type: ignore
        else:
            # For other years, show all months
            return [month.value.capitalize() for month in Month]

    def _update_month_dropdown(self) -> None:
        """Update the month dropdown values based on selected year."""
        available_months = self._get_available_months()
        self._month_dropdown.configure(values=available_months)  # type: ignore

        # Check if current selection is still valid
        current_month_str = self._month_var.get()
        if current_month_str not in available_months:
            # Reset to first available month if current selection is invalid
            if available_months:
                self._month_var.set(available_months[0])

    def _on_year_changed(self) -> None:
        """Handle year selection change."""
        self._update_month_dropdown()
        self._on_selection_changed()

    def _on_month_changed(self) -> None:
        """Handle month selection change."""
        self._on_selection_changed()

    def _on_selection_changed(self) -> None:
        month_str: str = self._month_var.get()
        selected_month: Optional[Month] = None

        for month in Month:
            if month.value.capitalize() == month_str:
                selected_month = month
                break

        try:
            selected_year: int = int(self._year_var.get())
        except ValueError:
            selected_year = self._current_year

        if selected_month and selected_year:
            selected_date: date = date(selected_year, selected_month.number, 1)
            today: date = date.today()

            if selected_date > today:
                self._month_var.set(self._current_month.value.capitalize())
                self._year_var.set(str(self._current_year))
                selected_month = self._current_month
                selected_year = self._current_year
                self._update_month_dropdown()

        self._on_date_changed(selected_month, selected_year)

    def get_selected_month(self) -> Optional[Month]:
        month_str: str = self._month_var.get()
        for month in Month:
            if month.value.capitalize() == month_str:
                return month
        return None

    def get_selected_year(self) -> Optional[int]:
        try:
            return int(self._year_var.get())
        except ValueError:
            return None

    def reset_to_current(self) -> None:
        self._month_var.set(self._current_month.value.capitalize())
        self._year_var.set(str(self._current_year))
        self._update_month_dropdown()
        self._on_selection_changed()
