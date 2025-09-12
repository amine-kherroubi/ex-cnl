from __future__ import annotations

# Standard library imports
from pathlib import Path
from tkinter import filedialog
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk


class FileSelector(ctk.CTkFrame):
    """Component for selecting input files."""

    def __init__(
        self, parent: Any, on_files_changed: Callable[[list[Path]], None]
    ) -> None:
        super().__init__(master=parent)

        self._on_files_changed: Callable[[list[Path]], None] = on_files_changed
        self._selected_files: list[Path] = []

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)

        # Label
        label = ctk.CTkLabel(
            self, text="Input Files:", font=ctk.CTkFont(size=14, weight="bold")
        )
        label.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")

        # Select files button
        self._select_button = ctk.CTkButton(
            self, text="Select Files", command=self._select_files, width=120
        )
        self._select_button.grid(row=0, column=2, padx=(5, 10), pady=10)

        # Files listbox
        self._files_listbox = ctk.CTkTextbox(self, height=100, state="disabled")
        self._files_listbox.grid(
            row=1, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="ew"
        )

        # Clear button
        self._clear_button = ctk.CTkButton(
            self,
            text="Clear",
            command=self._clear_files,
            width=80,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray80", "gray20"),
        )
        self._clear_button.grid(row=2, column=2, padx=(5, 10), pady=(0, 10))

        self._update_display()

    def _select_files(self) -> None:
        """Open file dialog to select files."""
        files = filedialog.askopenfilenames(
            title="Select Input Files",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        )

        if files:
            self._selected_files = [Path(file) for file in files]
            self._update_display()
            self._on_files_changed(self._selected_files)

    def _clear_files(self) -> None:
        """Clear selected files."""
        self._selected_files = []
        self._update_display()
        self._on_files_changed(self._selected_files)

    def _update_display(self) -> None:
        """Update the files display."""
        self._files_listbox.configure(state="normal")
        self._files_listbox.delete("1.0", "end")

        if self._selected_files:
            for file_path in self._selected_files:
                self._files_listbox.insert("end", f"📄 {file_path.name}\n")
                self._files_listbox.insert("end", f"   {file_path.parent}\n\n")
        else:
            self._files_listbox.insert("end", "No files selected")

        self._files_listbox.configure(state="disabled")

        # Update clear button state
        if self._selected_files:
            self._clear_button.configure(state="normal")
        else:
            self._clear_button.configure(state="disabled")
