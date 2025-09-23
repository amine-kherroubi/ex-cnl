from __future__ import annotations

# Standard library imports
from pathlib import Path
from tkinter import filedialog
from typing import Any, Callable, Literal

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.presentation.gui.components.base_component import BaseComponent
from app.presentation.gui.styling.design_system import DesignSystem


class FileSelector(BaseComponent):
    """Component for selecting source files."""

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
        self._on_files_changed: Callable[[list[Path]], None] = on_files_changed
        self._selected_files: list[Path] = []

        super().__init__(parent, "Fichiers source")

    def _setup_content(self) -> None:
        """Set up the file selector content."""
        # Configure grid
        self._content_frame.grid_columnconfigure(index=0, weight=1)

        # Title with select button row
        title_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self._content_frame, fg_color=DesignSystem.Color.TRANSPARENT
        )
        title_frame.grid(  # type: ignore
            row=0,
            column=0,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM),
            sticky="ew",
        )
        title_frame.grid_columnconfigure(index=0, weight=1)

        # Title
        title_label: ctk.CTkLabel = ctk.CTkLabel(
            master=title_frame,
            text=self._title,
            text_color=DesignSystem.Color.BLACK,
            font=ctk.CTkFont(size=DesignSystem.FontSize.H3, weight="bold"),
            anchor="w",
        )
        title_label.grid(row=0, column=0, sticky="w")  # type: ignore

        # Clear button - starts with disabled styling
        self._clear_button: ctk.CTkButton = ctk.CTkButton(
            master=title_frame,
            text="Réinitialiser",
            text_color=DesignSystem.Color.GRAY,
            fg_color=DesignSystem.Color.LESS_WHITE,
            hover_color=DesignSystem.Color.LEAST_WHITE,
            font=ctk.CTkFont(size=DesignSystem.FontSize.BUTTON),
            corner_radius=DesignSystem.Roundness.SM,
            height=DesignSystem.Height.SM,
            command=self._clear_files,
            width=DesignSystem.Width.SM,
        )
        self._clear_button.grid(row=0, column=1)  # type: ignore

        # Select files button
        self._select_button: ctk.CTkButton = ctk.CTkButton(
            master=title_frame,
            text="Sélectionner des fichiers",
            text_color=DesignSystem.Color.WHITE,
            fg_color=DesignSystem.Color.PRIMARY,
            hover_color=DesignSystem.Color.DARKER_PRIMARY,
            font=ctk.CTkFont(size=DesignSystem.FontSize.BUTTON),
            corner_radius=DesignSystem.Roundness.SM,
            height=DesignSystem.Height.SM,
            command=self._select_files,
            width=DesignSystem.Width.MD,
        )
        self._select_button.grid(  # type: ignore
            row=0, column=2, padx=(DesignSystem.Spacing.SM, DesignSystem.Spacing.NONE)
        )

        # Files listbox
        self._files_listbox: ctk.CTkTextbox = ctk.CTkTextbox(
            master=self._content_frame,
            height=100,
            state="disabled",
            corner_radius=DesignSystem.Roundness.SM,
            font=ctk.CTkFont(size=DesignSystem.FontSize.BODY),
        )
        self._files_listbox.grid(  # type: ignore
            row=1,
            column=0,
            columnspan=3,
            sticky="ew",
        )

        # Information text
        information: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text="Ajoutez vos fichiers Excel pour générer le rapport",
            font=ctk.CTkFont(size=DesignSystem.FontSize.CAPTION),
            text_color=DesignSystem.Color.GRAY,
        )
        information.grid(  # type: ignore
            row=2,
            columnspan=3,
            column=0,
            pady=(DesignSystem.Spacing.SM, DesignSystem.Spacing.NONE),
            sticky="w",
        )

        self._update_display()

    def _select_files(self) -> None:
        """Open file dialog to select files."""
        files: tuple[str, ...] | Literal[""] = filedialog.askopenfilenames(
            title="Sélectionner les fichiers source",
            filetypes=[
                ("Fichiers Excel", "*.xlsx"),
                ("Tous les types de fichiers", "*.*"),
            ],
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
        """Update the display of selected files."""
        self._files_listbox.configure(state="normal")  # type: ignore
        self._files_listbox.delete(index1="1.0", index2="end")  # type: ignore

        if self._selected_files:
            for file_path in self._selected_files:
                self._files_listbox.insert(  # type: ignore
                    index="end", text=f"Fichier : {file_path.name}\n"
                )
                self._files_listbox.insert(  # type: ignore
                    index="end", text=f"   {file_path.parent}\n\n"
                )
        else:
            self._files_listbox.insert(index="end", text="Aucun fichier sélectionné")  # type: ignore

        self._files_listbox.configure(state="disabled")  # type: ignore

        # Update clear button state and styling
        if self._selected_files:
            # Enable button with primary styling (yellow)
            self._clear_button.configure(  # type: ignore
                state="normal",
                text_color=DesignSystem.Color.WHITE,
                fg_color=DesignSystem.Color.GRAY,
                hover_color=DesignSystem.Color.DARKER_GRAY,
            )
        else:
            # Disable button with muted styling (gray)
            self._clear_button.configure(  # type: ignore
                state="disabled",
                text_color=DesignSystem.Color.GRAY,
                fg_color=DesignSystem.Color.LESS_WHITE,
                hover_color=DesignSystem.Color.LEAST_WHITE,
            )
