# Standard library imports
from pathlib import Path
from tkinter import filedialog
from typing import Any, Callable, Optional

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.presentation.gui.components.base_component import BaseComponent
from app.presentation.gui.styling.design_system import DesignSystem


class OutputSelector(BaseComponent):

    __slots__ = ("_on_output_changed", "_output_path", "_select_button", "_path_textbox")

    def __init__(
        self, parent: Any, on_output_changed: Callable[[Optional[Path]], None]
    ) -> None:
        self._on_output_changed: Callable[[Optional[Path]], None] = on_output_changed
        self._output_path: Optional[Path] = None

        super().__init__(parent, "Répertoire de destination")

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

        self._select_button: ctk.CTkButton = ctk.CTkButton(
            master=title_frame,
            text="Sélectionner un répertoire",
            text_color=DesignSystem.Color.WHITE.value,
            fg_color=DesignSystem.Color.PRIMARY.value,
            hover_color=DesignSystem.Color.DARKER_PRIMARY.value,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value, size=DesignSystem.FontSize.BUTTON.value,
            ),
            corner_radius=DesignSystem.Roundness.SM.value,
            height=DesignSystem.Height.SM.value,
            command=self._select_folder,
            width=DesignSystem.Width.MD.value,
        )
        self._select_button.grid(  # type: ignore
            row=0,
            column=1,
            padx=(DesignSystem.Spacing.MD.value, DesignSystem.Spacing.NONE.value),
        )

        information: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text="Choisissez le répertoire où sera enregistré le rapport généré",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value,
                size=DesignSystem.FontSize.CAPTION.value,
            ),
            text_color=DesignSystem.Color.GRAY.value,
        )
        information.grid(  # type: ignore
            row=1,
            column=0,
            pady=(DesignSystem.Spacing.NONE.value, DesignSystem.Spacing.SM.value),
            sticky="w",
        )

        self._path_textbox: ctk.CTkTextbox = ctk.CTkTextbox(
            master=self._content_frame,
            width=DesignSystem.Width.MD.value,
            height=DesignSystem.Height.SM.value,
            corner_radius=DesignSystem.Roundness.SM.value,
            border_width=DesignSystem.BorderWidth.XS.value,
            fg_color=DesignSystem.Color.LEAST_WHITE.value,
            border_color=DesignSystem.Color.LIGHTER_GRAY.value,
            text_color=DesignSystem.Color.GRAY.value,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value,
                size=DesignSystem.FontSize.BODY.value,
            ),
        )
        self._path_textbox.grid(row=2, column=0, sticky="ew")  # type: ignore
        self._path_textbox.insert("0.0", "Aucun répertoire selectionné")  # type: ignore
        self._path_textbox.configure(state="disabled")  # type: ignore

    def _select_folder(self) -> None:
        folder: str = filedialog.askdirectory(
            title="Sélectionner le répertoire de destination"
        )

        if folder:
            self._output_path = Path(folder)
            self._update_display()
            self._on_output_changed(self._output_path)

    def _update_display(self) -> None:
        self._path_textbox.configure(state="normal")  # type: ignore
        self._path_textbox.configure(text_color=DesignSystem.Color.BLACK.value)  # type: ignore
        self._path_textbox.delete("0.0", "end")  # type: ignore

        if self._output_path:
            self._path_textbox.insert("0.0", str(self._output_path))  # type: ignore
        else:
            self._path_textbox.insert("0.0", "")  # type: ignore

        self._path_textbox.configure(state="disabled")  # type: ignore