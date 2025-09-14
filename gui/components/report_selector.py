from __future__ import annotations

# Standard library imports
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.services.report_generation.models.report_specification import (
    ReportSpecification,
)


class ReportSelector(ctk.CTkFrame):
    __slots__ = (
        "_on_report_changed",
        "_reports",
        "_report_dropdown",
        "_description_text",
    )

    def __init__(
        self, parent: Any, on_report_changed: Callable[[str | None], None]
    ) -> None:
        super().__init__(master=parent)  # type: ignore

        self._on_report_changed: Callable[[str | None], None] = on_report_changed
        self._reports: dict[str, ReportSpecification] = {}

        self._setup_ui()

    def _setup_ui(self) -> None:
        # Configure grid
        self.grid_columnconfigure(index=1, weight=1)

        # Label
        label: ctk.CTkLabel = ctk.CTkLabel(
            master=self,
            text="Rapport à générer :",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        label.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")  # type: ignore

        # Report dropdown
        self._report_dropdown: ctk.CTkComboBox = ctk.CTkComboBox(
            master=self, values=[], command=self._on_report_selected, state="readonly"
        )
        self._report_dropdown.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="ew")  # type: ignore
        self._report_dropdown.set(value="Sélectionner un type de rapport")

        # Description text
        self._description_text: ctk.CTkTextbox = ctk.CTkTextbox(
            master=self, height=60, state="disabled"
        )
        self._description_text.grid(  # type: ignore
            row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew"
        )

    def set_reports(self, reports: dict[str, ReportSpecification]) -> None:
        self._reports = reports

        # Update dropdown values
        report_names: list[str] = list(reports.keys())
        self._report_dropdown.configure(values=report_names)  # type: ignore

        if report_names:
            self._report_dropdown.set(value="Sélectionner un type de rapport")
        else:
            self._report_dropdown.set(value="Aucun rapport disponible")

    def _on_report_selected(self, selection: str) -> None:
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
        self._description_text.configure(state="normal")  # type: ignore
        self._description_text.delete(index1="1.0", index2="end")  # type: ignore

        description_text: str = (
            f"Rapport : {report_spec.display_name}\n"
            f"Catégorie : {report_spec.category}\n"
            f"Fréquence : {report_spec.periodicity}\n"
            f"Description : {report_spec.description}"
        )

        self._description_text.insert(index="1.0", text=description_text)  # type: ignore
        self._description_text.configure(state="disabled")  # type: ignore

    def _clear_description(self) -> None:
        self._description_text.configure(state="normal")  # type: ignore
        self._description_text.delete(index1="1.0", index2="end")  # type: ignore
        self._description_text.insert(index="1.0", text="Sélectionner un type de rapport pour afficher les détails")  # type: ignore
        self._description_text.configure(state="disabled")  # type: ignore
