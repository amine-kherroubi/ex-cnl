from __future__ import annotations

# Standard library imports
from pathlib import Path
from tkinter import filedialog
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore


class OutputSelector(ctk.CTkFrame):
    def __init__(
        self, parent: Any, on_output_changed: Callable[[Path | None], None]
    ) -> None:
        super().__init__(parent)  # type: ignore

        self._on_output_changed: Callable[[Path | None], None] = on_output_changed
        self._output_path: Path | None = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)

        # Label
        label: ctk.CTkLabel = ctk.CTkLabel(
            master=self, text="Output Folder:", font=ctk.CTkFont(size=14, weight="bold")
        )
        label.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")  # type: ignore

        # Select folder button
        self._select_button: ctk.CTkButton = ctk.CTkButton(
            master=self, text="Select Folder", command=self._select_folder, width=120
        )
        self._select_button.grid(row=0, column=2, padx=(5, 10), pady=10)  # type: ignore

        # Path display
        self._path_entry: ctk.CTkEntry = ctk.CTkEntry(
            master=self, placeholder_text="No folder selected", state="readonly"
        )
        self._path_entry.grid(row=0, column=1, padx=(5, 5), pady=10, sticky="ew")  # type: ignore

    def _select_folder(self) -> None:
        folder: str = filedialog.askdirectory(title="Select Output Folder")

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
