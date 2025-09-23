from __future__ import annotations

# Standard library imports
from datetime import date
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.core.domain.enums.space_time import Month
from app.presentation.gui.components.base_component import BaseComponent
from app.presentation.gui.styling.design_system import DesignSystem


class DateSelector(BaseComponent):
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

        super().__init__(parent, "Période du rapport")

    def _setup_content(self) -> None:
        """Set up the date selector content."""
        # Configure grid
        self._content_frame.grid_columnconfigure(index=1, weight=1)
        self._content_frame.grid_columnconfigure(index=3, weight=1)

        # Title
        title: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text=self._title,
            text_color=DesignSystem.Color.BLACK,
            font=ctk.CTkFont(size=DesignSystem.FontSize.H3, weight="bold"),
            anchor="w",
        )
        title.grid(  # type: ignore
            row=0,
            column=0,
            columnspan=4,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.MD),
            sticky="w",
        )

        # Month label
        month_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text="Mois :",
            text_color=DesignSystem.Color.BLACK,
            font=ctk.CTkFont(size=DesignSystem.FontSize.BODY),
        )
        month_label.grid(  # type: ignore
            row=1,
            column=0,
            padx=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM),
            sticky="w",
        )

        # Month dropdown
        month_values: list[str] = [month.capitalize() for month in Month]
        self._month_dropdown: ctk.CTkComboBox = ctk.CTkComboBox(
            master=self._content_frame,
            values=month_values,
            variable=self._month_var,
            command=lambda _: self._on_selection_changed(),
            width=DesignSystem.Width.MD,
            height=DesignSystem.Height.SM,
            font=ctk.CTkFont(size=DesignSystem.FontSize.BODY),
            dropdown_font=ctk.CTkFont(size=DesignSystem.FontSize.BODY),
            state="readonly",
            corner_radius=DesignSystem.Roundness.SM,
        )
        self._month_dropdown.grid(  # type: ignore
            row=1,
            column=1,
            padx=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.MD),
            sticky="ew",
        )

        # Year label
        year_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text="Année :",
            text_color=DesignSystem.Color.BLACK,
            font=ctk.CTkFont(size=DesignSystem.FontSize.BODY),
        )
        year_label.grid(  # type: ignore
            row=1,
            column=2,
            padx=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM),
            sticky="w",
        )

        # Year dropdown - range from current year to 2000
        year_values: list[str] = [
            str(year) for year in range(self._current_year, 1999, -1)
        ]
        self._year_dropdown: ctk.CTkComboBox = ctk.CTkComboBox(
            master=self._content_frame,
            values=year_values,
            variable=self._year_var,
            command=lambda _: self._on_selection_changed(),
            width=DesignSystem.Width.MD,
            height=DesignSystem.Height.SM,
            font=ctk.CTkFont(size=DesignSystem.FontSize.BODY),
            dropdown_font=ctk.CTkFont(size=DesignSystem.FontSize.BODY),
            state="readonly",
            corner_radius=DesignSystem.Roundness.SM,
        )
        self._year_dropdown.grid(row=1, column=3, sticky="ew")  # type: ignore

        # Information text
        information: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text="Sélectionnez la période pour laquelle vous souhaitez générer le rapport",
            font=ctk.CTkFont(size=DesignSystem.FontSize.CAPTION),
            text_color=DesignSystem.Color.GRAY,
        )
        information.grid(  # type: ignore
            row=2,
            columnspan=4,
            column=0,
            pady=(DesignSystem.Spacing.SM, DesignSystem.Spacing.NONE),
            sticky="w",
        )

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
