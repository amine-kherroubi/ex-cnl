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

        self._content_frame.grid_columnconfigure(index=0, weight=1)

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

        title_label: ctk.CTkLabel = ctk.CTkLabel(
            master=title_frame,
            text=self._title,
            text_color=DesignSystem.Color.BLACK,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.H3,
                weight="bold",
            ),
            anchor="w",
        )
        title_label.grid(row=0, column=0, sticky="w")  # type: ignore

        self._clear_button: ctk.CTkButton = ctk.CTkButton(
            master=title_frame,
            text="Réinitialiser",
            text_color=DesignSystem.Color.GRAY,
            fg_color=DesignSystem.Color.LESS_WHITE,
            hover_color=DesignSystem.Color.LEAST_WHITE,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL, size=DesignSystem.FontSize.BUTTON
            ),
            corner_radius=DesignSystem.Roundness.SM,
            height=DesignSystem.Height.SM,
            command=self._clear_files,
            width=DesignSystem.Width.SM,
        )
        self._clear_button.grid(row=0, column=1)  # type: ignore

        self._select_button: ctk.CTkButton = ctk.CTkButton(
            master=title_frame,
            text="Sélectionner des fichiers",
            text_color=DesignSystem.Color.WHITE,
            fg_color=DesignSystem.Color.PRIMARY,
            hover_color=DesignSystem.Color.DARKER_PRIMARY,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL, size=DesignSystem.FontSize.BUTTON
            ),
            corner_radius=DesignSystem.Roundness.SM,
            height=DesignSystem.Height.SM,
            command=self._select_files,
            width=DesignSystem.Width.MD,
        )
        self._select_button.grid(  # type: ignore
            row=0, column=2, padx=(DesignSystem.Spacing.SM, DesignSystem.Spacing.NONE)
        )

        info_text: str = (
            "Ajoutez les fichiers Excel nécessaires pour générer le rapport. "
        )
        information: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text=info_text,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.CAPTION,
            ),
            text_color=DesignSystem.Color.GRAY,
            wraplength=400,  # Allow text wrapping for longer description
        )
        information.grid(  # type: ignore
            row=1,
            columnspan=3,
            column=0,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM),
            sticky="w",
        )

        self._files_listbox: ctk.CTkTextbox = ctk.CTkTextbox(
            master=self._content_frame,
            height=100,
            state="disabled",
            border_width=DesignSystem.BorderWidth.XS,
            corner_radius=DesignSystem.Roundness.SM,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL, size=DesignSystem.FontSize.BODY
            ),
        )
        self._files_listbox.grid(  # type: ignore
            row=2,
            column=0,
            columnspan=3,
            sticky="ew",
        )

        self._update_display()

    def _select_files(self) -> None:

        files: tuple[str, ...] | Literal[""] = filedialog.askopenfilenames(
            title="Sélectionner les fichiers source",
            filetypes=[
                ("Fichiers Excel", "*.xlsx"),
                ("Tous les types de fichiers", "*.*"),
            ],
        )

        if files:

            new_files: list[Path] = [Path(file) for file in files]

            existing_paths: set[Path] = set(self._selected_files)

            added_files: list[Path] = []
            for file_path in new_files:
                if file_path not in existing_paths:
                    self._selected_files.append(file_path)
                    added_files.append(file_path)

            if (
                added_files or not self._selected_files
            ):  # Update even if no new files to refresh display
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

            count_text: str = (
                f"Fichiers sélectionnés ({len(self._selected_files)}):\n\n"
            )
            self._files_listbox.insert(index="end", text=count_text)  # type: ignore

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

        if self._selected_files:

            self._clear_button.configure(  # type: ignore
                state="normal",
                text_color=DesignSystem.Color.WHITE,
                fg_color=DesignSystem.Color.GRAY,
                hover_color=DesignSystem.Color.DARKER_GRAY,
            )
        else:

            self._clear_button.configure(  # type: ignore
                state="disabled",
                text_color=DesignSystem.Color.GRAY,
                fg_color=DesignSystem.Color.LESS_WHITE,
                hover_color=DesignSystem.Color.LEAST_WHITE,
            )
