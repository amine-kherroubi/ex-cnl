from __future__ import annotations

# Standard library imports
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk


class ReportSelector(ctk.CTkFrame):
    """Component for selecting report type."""

    def __init__(
        self, parent: Any, on_report_changed: Callable[[str | None], None]
    ) -> None:
        super().__init__(parent)

        self._on_report_changed: Callable[[str | None], None] = on_report_changed
        self._reports: dict[str, Any] = {}

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)

        # Label
        label = ctk.CTkLabel(
            self, text="Report Type:", font=ctk.CTkFont(size=14, weight="bold")
        )
        label.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")

        # Report dropdown
        self._report_dropdown = ctk.CTkComboBox(
            self, values=[], command=self._on_report_selected, state="readonly"
        )
        self._report_dropdown.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="ew")
        self._report_dropdown.set("Select a report type...")

        # Description text
        self._description_text = ctk.CTkTextbox(self, height=60, state="disabled")
        self._description_text.grid(
            row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew"
        )

    def set_reports(self, reports: dict[str, Any]) -> None:
        """Set available reports."""
        self._reports = reports

        # Update dropdown values
        report_names = list(reports.keys())
        self._report_dropdown.configure(values=report_names)

        if report_names:
            self._report_dropdown.set("Select a report type...")
        else:
            self._report_dropdown.set("No reports available")

    def _on_report_selected(self, selection: str) -> None:
        """Handle report selection."""
        if (
            selection == "Select a report type..."
            or selection == "No reports available"
        ):
            self._clear_description()
            self._on_report_changed(None)
            return

        # Update description
        if selection in self._reports:
            report_spec = self._reports[selection]
            self._update_description(report_spec)
            self._on_report_changed(selection)
        else:
            self._clear_description()
            self._on_report_changed(None)

    def _update_description(self, report_spec: Any) -> None:
        """Update the report description display."""
        self._description_text.configure(state="normal")
        self._description_text.delete("1.0", "end")

        # Extract description from report specification
        description = getattr(report_spec, "description", "No description available")
        display_name = getattr(report_spec, "display_name", "Unknown Report")
        category = getattr(report_spec, "category", "Unknown Category")
        periodicity = getattr(report_spec, "periodicity", "Unknown Frequency")

        description_text = f"📊 {display_name}\n"
        description_text += f"📁 Category: {category}\n"
        description_text += f"⏰ Frequency: {periodicity}\n"
        description_text += f"📝 {description}"

        self._description_text.insert("1.0", description_text)
        self._description_text.configure(state="disabled")

    def _clear_description(self) -> None:
        """Clear the description display."""
        self._description_text.configure(state="normal")
        self._description_text.delete("1.0", "end")
        self._description_text.insert("1.0", "Select a report type to see details")
        self._description_text.configure(state="disabled")
