from __future__ import annotations

# Standard library imports
from datetime import date
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.core.domain.enums.space_time import Month
from app.presentation.gui.styling.design_system import Color, Spacing, FontSize


class DateSelector(ctk.CTkFrame):
    """Component for selecting month and year for report generation."""

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
        on_date_changed: Callable[[Month | None, int | None], None],
    ) -> None:
        super().__init__(master=parent)  # type: ignore
        self._on_date_changed: Callable[[Month | None, int | None], None] = (
            on_date_changed
        )

        # Get current date
        today: date = date.today()
        self._current_month: Month = Month.from_number(today.month)
        self._current_year: int = today.year

        # Initialize variables
        self._month_var: ctk.StringVar = ctk.StringVar(
            value=self._current_month.capitalize()
        )
        self._year_var: ctk.StringVar = ctk.StringVar(value=str(self._current_year))

        self._setup_ui()

    def _setup_ui(self) -> None:
        # Configure frame
        self.configure(fg_color=Color.TRANSPARENT)  # type: ignore
        self.grid_columnconfigure(index=1, weight=1)
        self.grid_columnconfigure(index=3, weight=1)

        # Title
        title_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self,
            text="Période du rapport",
            font=ctk.CTkFont(size=FontSize.LABEL, weight="bold"),
        )
        title_label.grid(row=0, column=0, columnspan=4, pady=(Spacing.NONE, Spacing.SM), sticky="w")  # type: ignore

        # Month label
        month_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self,
            text="Mois :",
            font=ctk.CTkFont(size=FontSize.BODY),
        )
        month_label.grid(row=1, column=0, padx=(Spacing.NONE, Spacing.SM), sticky="w")  # type: ignore

        # Month dropdown
        month_values: list[str] = [month.capitalize() for month in Month]
        self._month_dropdown: ctk.CTkComboBox = ctk.CTkComboBox(
            master=self,
            values=month_values,
            variable=self._month_var,
            command=lambda _: self._on_selection_changed(),
            width=140,
            height=32,
            font=ctk.CTkFont(size=FontSize.BODY),
            dropdown_font=ctk.CTkFont(size=FontSize.BODY),
            state="readonly",
        )
        self._month_dropdown.grid(row=1, column=1, padx=(Spacing.NONE, Spacing.MD), sticky="ew")  # type: ignore

        # Year label
        year_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self,
            text="Année :",
            font=ctk.CTkFont(size=FontSize.BODY),
        )
        year_label.grid(row=1, column=2, padx=(Spacing.NONE, Spacing.SM), sticky="w")  # type: ignore

        # Year dropdown - range from 2000 to current year
        year_values: list[str] = [
            str(year) for year in range(self._current_year, 1999, -1)
        ]
        self._year_dropdown: ctk.CTkComboBox = ctk.CTkComboBox(
            master=self,
            values=year_values,
            variable=self._year_var,
            command=lambda _: self._on_selection_changed(),
            width=100,
            height=32,
            font=ctk.CTkFont(size=FontSize.BODY),
            dropdown_font=ctk.CTkFont(size=FontSize.BODY),
            state="readonly",
        )
        self._year_dropdown.grid(row=1, column=3, sticky="w")  # type: ignore

        # Info text
        info_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self,
            text="Sélectionnez la période pour laquelle vous souhaitez générer le rapport",
            font=ctk.CTkFont(size=FontSize.LABEL),
            text_color="gray60",
        )
        info_label.grid(row=2, column=0, columnspan=4, pady=(Spacing.SM, Spacing.NONE), sticky="w")  # type: ignore

    def _on_selection_changed(self) -> None:
        """Handle month or year selection change."""
        # Get selected month
        month_str: str = self._month_var.get()
        selected_month: Month | None = None

        for month in Month:
            if month.capitalize() == month_str:
                selected_month = month
                break

        # Get selected year
        try:
            selected_year: int = int(self._year_var.get())
        except ValueError:
            selected_year = self._current_year

        # Validate that selected date is not in the future
        if selected_month and selected_year:
            selected_date: date = date(selected_year, selected_month.number, 1)
            today: date = date.today()

            if selected_date > today:
                # Reset to current month/year if future date selected
                self._month_var.set(self._current_month.capitalize())
                self._year_var.set(str(self._current_year))
                selected_month = self._current_month
                selected_year = self._current_year

        # Notify parent of change
        self._on_date_changed(selected_month, selected_year)

    def get_selected_month(self) -> Month | None:
        """Get the currently selected month."""
        month_str: str = self._month_var.get()
        for month in Month:
            if month.capitalize() == month_str:
                return month
        return None

    def get_selected_year(self) -> int | None:
        """Get the currently selected year."""
        try:
            return int(self._year_var.get())
        except ValueError:
            return None

    def reset_to_current(self) -> None:
        """Reset selection to current month and year."""
        self._month_var.set(self._current_month.capitalize())
        self._year_var.set(str(self._current_year))
        self._on_selection_changed()
