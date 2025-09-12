from __future__ import annotations

# Standard library imports
from pathlib import Path
from tkinter import filedialog
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk


class OutputSelector(ctk.CTkFrame):
    """Component for selecting output folder."""

    def __init__(
        self, parent: Any, on_output_changed: Callable[[Path | None], None]
    ) -> None:
        super().__init__(parent)

        self._on_output_changed: Callable[[Path | None], None] = on_output_changed
        self._output_path: Path | None = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)

        # Label
        label = ctk.CTkLabel(
            self, text="Output Folder:", font=ctk.CTkFont(size=14, weight="bold")
        )
        label.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")

        # Select folder button
        self._select_button = ctk.CTkButton(
            self, text="Select Folder", command=self._select_folder, width=120
        )
        self._select_button.grid(row=0, column=2, padx=(5, 10), pady=10)

        # Path display
        self._path_entry = ctk.CTkEntry(
            self, placeholder_text="No folder selected", state="readonly"
        )
        self._path_entry.grid(row=0, column=1, padx=(5, 5), pady=10, sticky="ew")

    def _select_folder(self) -> None:
        """Open folder dialog to select output folder."""
        folder = filedialog.askdirectory(title="Select Output Folder")

        if folder:
            self._output_path = Path(folder)
            self._update_display()
            self._on_output_changed(self._output_path)

    def _update_display(self) -> None:
        """Update the path display."""
        self._path_entry.configure(state="normal")
        self._path_entry.delete(0, "end")

        if self._output_path:
            self._path_entry.insert(0, str(self._output_path))
        else:
            self._path_entry.insert(0, "")

        self._path_entry.configure(state="readonly")
