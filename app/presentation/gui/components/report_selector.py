from __future__ import annotations

# Standard library imports
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.core.domain.models.report_specification import ReportSpecification
from app.presentation.gui.components.base_component import BaseComponent
from app.presentation.gui.styling.design_system import DesignSystem


class ReportSelector(BaseComponent):
    """Component for selecting report type."""

    __slots__ = (
        "_on_report_changed",
        "_reports",
        "_report_dropdown",
        "_description_text",
    )

    def __init__(
        self, parent: Any, on_report_changed: Callable[[str | None], None]
    ) -> None:
        self._on_report_changed: Callable[[str | None], None] = on_report_changed
        self._reports: dict[str, ReportSpecification] = {}

        super().__init__(parent, "Rapport à générer")

    def _setup_content(self) -> None:
        """Set up the report selector content."""
        # Configure grid
        self._content_frame.grid_columnconfigure(index=1, weight=1)

        # Title with dropdown row
        selector_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self._content_frame, fg_color=DesignSystem.Color.TRANSPARENT
        )
        selector_frame.grid(  # type: ignore
            row=0,
            column=0,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM),
            sticky="ew",
        )
        selector_frame.grid_columnconfigure(index=1, weight=1)

        # Title
        title_label: ctk.CTkLabel = ctk.CTkLabel(
            master=selector_frame,
            text=f"{self._title} :",
            text_color=DesignSystem.Color.BLACK,
            font=ctk.CTkFont(size=DesignSystem.FontSize.H3, weight="bold"),
            anchor="w",
        )
        title_label.grid(  # type: ignore
            row=0,
            column=0,
            padx=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM),
            sticky="w",
        )

        # Report dropdown
        self._report_dropdown: ctk.CTkComboBox = ctk.CTkComboBox(
            master=selector_frame,
            values=[],
            command=self._on_report_selected,
            state="readonly",
            height=DesignSystem.Height.SM,
            font=ctk.CTkFont(size=DesignSystem.FontSize.BODY),
            dropdown_font=ctk.CTkFont(size=DesignSystem.FontSize.BODY),
            corner_radius=DesignSystem.Roundness.SM,
        )
        self._report_dropdown.grid(row=0, column=1, sticky="ew")  # type: ignore
        self._report_dropdown.set(value="Sélectionner un type de rapport")

        # Description text
        self._description_text: ctk.CTkTextbox = ctk.CTkTextbox(
            master=self._content_frame,
            height=80,
            state="disabled",
            corner_radius=DesignSystem.Roundness.SM,
            font=ctk.CTkFont(size=DesignSystem.FontSize.BODY),
        )
        self._description_text.grid(  # type: ignore
            row=1,
            column=0,
            sticky="ew",
        )

        self._clear_description()

    def set_reports(self, reports: dict[str, ReportSpecification]) -> None:
        """Set available reports and update dropdown."""
        self._reports = reports

        # Update dropdown values
        report_names: list[str] = list(reports.keys())
        self._report_dropdown.configure(values=report_names)  # type: ignore

        if report_names:
            self._report_dropdown.set(value="Sélectionner un type de rapport")
        else:
            self._report_dropdown.set(value="Aucun rapport disponible")

    def _on_report_selected(self, selection: str) -> None:
        """Handle report selection change."""
        if (
            selection == "Sélectionner un type de rapport"
            or selection == "Aucun rapport disponible"
        ):
            self._clear_description()
            self._on_report_changed(None)
            return

        # Update description
        if selection in self._reports:
            report_spec: ReportSpecification = self._reports[selection]
            self._update_description(report_spec)
            self._on_report_changed(selection)
        else:
            self._clear_description()
            self._on_report_changed(None)

    def _update_description(self, report_spec: ReportSpecification) -> None:
        """Update description text with report details."""
        self._description_text.configure(state="normal")  # type: ignore
        self._description_text.delete(index1="1.0", index2="end")  # type: ignore

        description_text: str = (
            f"Rapport : {report_spec.display_name}\n"
            f"Catégorie : {report_spec.category}\n"
            f"Description : {report_spec.description}"
        )

        self._description_text.insert(index="1.0", text=description_text)  # type: ignore
        self._description_text.configure(state="disabled")  # type: ignore

    def _clear_description(self) -> None:
        """Clear description text."""
        self._description_text.configure(state="normal")  # type: ignore
        self._description_text.delete(index1="1.0", index2="end")  # type: ignore
        self._description_text.insert(  # type: ignore
            index="1.0",
            text="Sélectionner un type de rapport pour afficher les détails",
        )
        self._description_text.configure(state="disabled")  # type: ignore
