from __future__ import annotations

# Standard library imports
from pathlib import Path
from tkinter import filedialog
from typing import Any, Callable, Literal

# Third-party imports
import customtkinter as ctk  # type: ignore


class FileSelector(ctk.CTkFrame):
    __slots__ = (
        "_on_files_changed",
        "_selected_files",
        "_select_button",
        "_files_listbox",
        "_clear_button",
    )

    def __init__(
        self, parent: Any, on_files_changed: Callable[[list[Path]], None]
    ) -> None:
        super().__init__(master=parent)  # type: ignore

        self._on_files_changed: Callable[[list[Path]], None] = on_files_changed
        self._selected_files: list[Path] = []

        self._setup_ui()

    def _setup_ui(self) -> None:
        # Configure grid
        self.grid_columnconfigure(index=1, weight=1)

        # Label
        label: ctk.CTkLabel = ctk.CTkLabel(
            master=self, text="Input Files:", font=ctk.CTkFont(size=14, weight="bold")
        )
        label.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")  # type: ignore

        # Select files button
        self._select_button: ctk.CTkButton = ctk.CTkButton(
            master=self, text="Select Files", command=self._select_files, width=120
        )
        self._select_button.grid(row=0, column=2, padx=(5, 10), pady=10)  # type: ignore

        # Files listbox
        self._files_listbox: ctk.CTkTextbox = ctk.CTkTextbox(
            master=self, height=100, state="disabled"
        )
        self._files_listbox.grid(  # type: ignore
            row=1, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="ew"
        )

        # Clear button
        self._clear_button: ctk.CTkButton = ctk.CTkButton(
            master=self,
            text="Clear",
            command=self._clear_files,
            width=80,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray80", "gray20"),
        )
        self._clear_button.grid(row=2, column=2, padx=(5, 10), pady=(0, 10))  # type: ignore

        self._update_display()

    def _select_files(self) -> None:
        files: tuple[str, ...] | Literal[""] = filedialog.askopenfilenames(
            title="Select Input Files",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        )

        if files:
            self._selected_files = [Path(file) for file in files]
            self._update_display()
            self._on_files_changed(self._selected_files)

    def _clear_files(self) -> None:
        self._selected_files = []
        self._update_display()
        self._on_files_changed(self._selected_files)

    def _update_display(self) -> None:
        self._files_listbox.configure(state="normal")  # type: ignore
        self._files_listbox.delete(index1="1.0", index2="end")  # type: ignore

        if self._selected_files:
            for file_path in self._selected_files:
                self._files_listbox.insert(index="end", text=f"File: {file_path.name}\n")  # type: ignore
                self._files_listbox.insert(index="end", text=f"   {file_path.parent}\n\n")  # type: ignore
        else:
            self._files_listbox.insert(index="end", text="No files selected")  # type: ignore

        self._files_listbox.configure(state="disabled")  # type: ignore

        # Update clear button state
        if self._selected_files:
            self._clear_button.configure(state="normal")  # type: ignore
        else:
            self._clear_button.configure(state="disabled")  # type: ignore
