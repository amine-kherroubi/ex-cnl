from __future__ import annotations

# Standard library imports
from pathlib import Path
from tkinter import filedialog
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.presentation.gui.styling.design_system import DesignSystem


class OutputSelector(ctk.CTkFrame):
    __slots__ = ("_on_output_changed", "_output_path", "_select_button", "_path_entry")

    def __init__(
        self, parent: Any, on_output_changed: Callable[[Path | None], None]
    ) -> None:
        super().__init__(master=parent)  # type: ignore

        self._on_output_changed: Callable[[Path | None], None] = on_output_changed
        self._output_path: Path | None = None

        # Configure grid
        self.grid_columnconfigure(index=1, weight=1)

        # Label
        label: ctk.CTkLabel = ctk.CTkLabel(
            master=self,
            text="Répertoire de destination",
            font=ctk.CTkFont(size=DesignSystem.FontSize.LABEL, weight="bold"),
        )
        label.grid(row=0, column=0, padx=(DesignSystem.Spacing.SM, DesignSystem.Spacing.XS), pady=DesignSystem.Spacing.SM, sticky="w")  # type: ignore

        # Select folder button
        self._select_button: ctk.CTkButton = ctk.CTkButton(
            master=self,
            text="Sélectionner un répertoire",
            command=self._select_folder,
            width=120,
        )
        self._select_button.grid(row=0, column=2, padx=(DesignSystem.Spacing.XS, DesignSystem.Spacing.SM), pady=DesignSystem.Spacing.SM)  # type: ignore

        # Path display
        self._path_entry: ctk.CTkEntry = ctk.CTkEntry(
            master=self,
            placeholder_text="Aucun répertoire sélectionné",
            state="readonly",
        )
        self._path_entry.grid(row=0, column=1, padx=(DesignSystem.Spacing.XS, DesignSystem.Spacing.XS), pady=DesignSystem.Spacing.SM, sticky="ew")  # type: ignore

    def _select_folder(self) -> None:
        folder: str = filedialog.askdirectory(
            title="Sélectionner le répertoire de destination"
        )

        if folder:
            self._output_path = Path(folder)
            self._update_display()
            self._on_output_changed(self._output_path)

    def _update_display(self) -> None:
        self._path_entry.configure(state="normal")  # type: ignore
        self._path_entry.delete(first_index=0, last_index="end")  # type: ignore

        if self._output_path:
            self._path_entry.insert(index=0, string=str(self._output_path))  # type: ignore
        else:
            self._path_entry.insert(index=0, string="")  # type: ignore

        self._path_entry.configure(state="readonly")  # type: ignore
