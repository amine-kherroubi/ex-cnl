from __future__ import annotations

# Standard library imports
from pathlib import Path
from tkinter import filedialog
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.presentation.gui.components.base_component import BaseComponent
from app.presentation.gui.styling.design_system import DesignSystem


class OutputSelector(BaseComponent):
    """Component for selecting output directory."""

    __slots__ = ("_on_output_changed", "_output_path", "_select_button", "_path_entry")

    def __init__(
        self, parent: Any, on_output_changed: Callable[[Path | None], None]
    ) -> None:
        self._on_output_changed: Callable[[Path | None], None] = on_output_changed
        self._output_path: Path | None = None

        super().__init__(parent, "Répertoire de destination")

    def _setup_content(self) -> None:
        """Set up the output selector content."""
        # Configure grid
        self._content_frame.grid_columnconfigure(index=1, weight=1)

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

        # Select folder button
        self._select_button: ctk.CTkButton = ctk.CTkButton(
            master=title_frame,
            text="Sélectionner un répertoire",
            text_color=DesignSystem.Color.WHITE,
            fg_color=DesignSystem.Color.PRIMARY,
            hover_color=DesignSystem.Color.DARKER_PRIMARY,
            font=ctk.CTkFont(size=DesignSystem.FontSize.BUTTON),
            corner_radius=DesignSystem.Roundness.SM,
            height=DesignSystem.Height.SM,
            command=self._select_folder,
            width=DesignSystem.Width.MD,
        )
        self._select_button.grid(  # type: ignore
            row=0,
            column=1,
            padx=(DesignSystem.Spacing.MD, DesignSystem.Spacing.NONE),
            sticky="ew",
        )

        # Path display
        self._path_entry: ctk.CTkEntry = ctk.CTkEntry(
            master=self._content_frame,
            placeholder_text="Aucun répertoire sélectionné",
            corner_radius=DesignSystem.Roundness.SM,
            height=DesignSystem.Height.SM,
            font=ctk.CTkFont(size=DesignSystem.FontSize.BODY),
        )
        self._path_entry.grid(row=1, column=0, columnspan=2, sticky="ew")  # type: ignore

        # Information text
        information: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text="Choisissez le répertoire où sera enregistré le rapport généré",
            font=ctk.CTkFont(size=DesignSystem.FontSize.CAPTION),
            text_color=DesignSystem.Color.GRAY,
        )
        information.grid(  # type: ignore
            row=2,
            columnspan=2,
            column=0,
            pady=(DesignSystem.Spacing.SM, DesignSystem.Spacing.NONE),
            sticky="w",
        )

    def _select_folder(self) -> None:
        """Open directory dialog to select output folder."""
        folder: str = filedialog.askdirectory(
            title="Sélectionner le répertoire de destination"
        )

        if folder:
            self._output_path = Path(folder)
            self._update_display()
            self._on_output_changed(self._output_path)

    def _update_display(self) -> None:
        """Update the display of selected path."""
        self._path_entry.configure(state="normal")  # type: ignore
        self._path_entry.delete(first_index=0, last_index="end")  # type: ignore

        if self._output_path:
            self._path_entry.insert(index=0, string=str(self._output_path))  # type: ignore
        else:
            self._path_entry.insert(index=0, string="")  # type: ignore
