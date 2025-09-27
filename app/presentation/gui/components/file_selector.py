

# Standard library imports
from pathlib import Path
from tkinter import filedialog
from typing import Any, Callable, Literal, Tuple, Union, List

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
        self, parent: Any, on_files_changed: Callable[[List[Path]], None]
    ) -> None:
        self._on_files_changed: Callable[[list[Path]], None] = on_files_changed
        self._selected_files: list[Path] = []

        super().__init__(parent, "Fichiers source")

    def _setup_content(self) -> None:

        self._content_frame.grid_columnconfigure(index=0, weight=1)

        title_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self._content_frame, fg_color=DesignSystem.Color.TRANSPARENT.value
        )
        title_frame.grid(  # type: ignore
            row=0,
            column=0,
            pady=(DesignSystem.Spacing.NONE.value, DesignSystem.Spacing.SM.value),
            sticky="ew",
        )
        title_frame.grid_columnconfigure(index=0, weight=1)

        title_label: ctk.CTkLabel = ctk.CTkLabel(
            master=title_frame,
            text=self._title,
            text_color=DesignSystem.Color.BLACK.value,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value,
                size=DesignSystem.FontSize.H3.value,
                weight="bold",
            ),
            anchor="w",
        )
        title_label.grid(row=0, column=0, sticky="w")  # type: ignore

        self._clear_button: ctk.CTkButton = ctk.CTkButton(
            master=title_frame,
            text="Réinitialiser",
            text_color=DesignSystem.Color.GRAY.value,
            fg_color=DesignSystem.Color.LESS_WHITE.value,
            hover_color=DesignSystem.Color.LEAST_WHITE.value,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value, size=DesignSystem.FontSize.BUTTON.value,
            ),
            corner_radius=DesignSystem.Roundness.SM.value,
            height=DesignSystem.Height.SM.value,
            command=self._clear_files,
            width=DesignSystem.Width.SM.value,
        )
        self._clear_button.grid(row=0, column=1)  # type: ignore

        self._select_button: ctk.CTkButton = ctk.CTkButton(
            master=title_frame,
            text="Sélectionner des fichiers",
            text_color=DesignSystem.Color.WHITE.value,
            fg_color=DesignSystem.Color.PRIMARY.value,
            hover_color=DesignSystem.Color.DARKER_PRIMARY.value,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value, size=DesignSystem.FontSize.BUTTON.value,
            ),
            corner_radius=DesignSystem.Roundness.SM.value,
            height=DesignSystem.Height.SM.value,
            command=self._select_files,
            width=DesignSystem.Width.MD.value,
        )
        self._select_button.grid(  # type: ignore
            row=0, column=2, padx=(DesignSystem.Spacing.SM.value, DesignSystem.Spacing.NONE.value)
        )

        info_text: str = (
            "Ajoutez les fichiers Excel nécessaires pour générer le rapport. "
        )
        information: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text=info_text,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value,
                size=DesignSystem.FontSize.CAPTION.value,
            ),
            text_color=DesignSystem.Color.GRAY.value,
            wraplength=400,  # Allow text wrapping for longer description
        )
        information.grid(  # type: ignore
            row=1,
            columnspan=3,
            column=0,
            pady=(DesignSystem.Spacing.NONE.value, DesignSystem.Spacing.SM.value),
            sticky="w",
        )

        self._files_listbox: ctk.CTkTextbox = ctk.CTkTextbox(
            master=self._content_frame,
            height=100,
            state="disabled",
            border_width=DesignSystem.BorderWidth.XS.value,
            corner_radius=DesignSystem.Roundness.SM.value,
            text_color=DesignSystem.Color.GRAY.value,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value, size=DesignSystem.FontSize.BODY.value
            ),
            fg_color=DesignSystem.Color.LEAST_WHITE.value,
            border_color=DesignSystem.Color.LIGHTER_GRAY.value,
        )
        self._files_listbox.grid(  # type: ignore
            row=2,
            column=0,
            columnspan=3,
            sticky="ew",
        )

        self._update_display()

    def _select_files(self) -> None:
        files: Union[Tuple[str, ...], Literal[""]] = filedialog.askopenfilenames(
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
            self._files_listbox.configure(text_color=DesignSystem.Color.BLACK.value)  # type: ignore

            for i, file_path in enumerate(self._selected_files):
                self._files_listbox.insert(  # type: ignore
                    index="end", text=f"{i + 1} - {file_path}\n"
                )
        else:
            self._files_listbox.configure(text_color=DesignSystem.Color.GRAY.value)  # type: ignore
            self._files_listbox.insert(index="end", text="Aucun fichier sélectionné")  # type: ignore

        self._files_listbox.configure(state="disabled")  # type: ignore

        if self._selected_files:
            self._clear_button.configure(  # type: ignore
                state="normal",
                text_color=DesignSystem.Color.WHITE.value,
                fg_color=DesignSystem.Color.GRAY.value,
                hover_color=DesignSystem.Color.DARKER_GRAY.value,
            )
        else:
            self._clear_button.configure(  # type: ignore
                state="disabled",
                text_color=DesignSystem.Color.GRAY.value,
                fg_color=DesignSystem.Color.LESS_WHITE.value,
                hover_color=DesignSystem.Color.LEAST_WHITE.value,
            )
