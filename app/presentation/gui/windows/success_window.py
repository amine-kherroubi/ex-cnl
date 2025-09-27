from __future__ import annotations

# Standard library imports
import platform
import subprocess
from pathlib import Path
from typing import Any

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.presentation.gui.styling.design_system import DesignSystem


class SuccessWindow(ctk.CTkToplevel):

    __slots__ = (
        "_output_file_path",
        "_content_frame",
    )

    def __init__(
        self,
        parent: Any,
        output_file_path: Path,
    ) -> None:
        super().__init__(master=parent)  # type: ignore

        self._output_file_path: Path = output_file_path

        self._setup_window()
        self._setup_ui()
        self._auto_size_window()

    def _setup_window(self) -> None:

        self.title("Rapport généré avec succès")
        self.resizable(False, False)
        self.transient(self.master)  # type: ignore
        self.configure(fg_color=DesignSystem.Color.WHITE)  # type: ignore

        self.grid_columnconfigure(index=0, weight=1)
        self.grid_rowconfigure(index=0, weight=1)

    def _setup_ui(self) -> None:

        self._content_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self,
            fg_color=DesignSystem.Color.WHITE,
            border_width=DesignSystem.BorderWidth.XS,
            border_color=DesignSystem.Color.LIGHTER_GRAY,
            corner_radius=DesignSystem.Roundness.MD,
        )
        self._content_frame.grid(  # type: ignore
            row=0,
            column=0,
            padx=DesignSystem.Spacing.XXL,
            pady=DesignSystem.Spacing.XXL,
            sticky="nsew",
        )
        self._content_frame.grid_columnconfigure(index=0, weight=1)

        inner_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self._content_frame, fg_color=DesignSystem.Color.TRANSPARENT
        )
        inner_frame.grid(  # type: ignore
            row=0,
            column=0,
            padx=DesignSystem.Spacing.LG,
            pady=DesignSystem.Spacing.LG,
            sticky="nsew",
        )
        inner_frame.grid_columnconfigure(index=0, weight=1)

        title: ctk.CTkLabel = ctk.CTkLabel(
            master=inner_frame,
            text="Rapport généré avec succès !",
            text_color=DesignSystem.Color.BLACK,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.H1,
                weight="bold",
            ),
        )
        title.grid(  # type: ignore
            row=0,
            column=0,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.MD),
            sticky="ew",
        )

        message: ctk.CTkLabel = ctk.CTkLabel(
            master=inner_frame,
            text="Le rapport a été généré et sauvegardé dans le répertoire spécifié",
            text_color=DesignSystem.Color.BLACK,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.BODY,
            ),
        )
        message.grid(  # type: ignore
            row=1,
            column=0,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.LG),
            sticky="ew",
        )

        file_info_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=inner_frame,
            fg_color=DesignSystem.Color.LEAST_WHITE,
            corner_radius=DesignSystem.Roundness.SM,
        )
        file_info_frame.grid(  # type: ignore
            row=2,
            column=0,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.LG),
            sticky="ew",
        )
        file_info_frame.grid_columnconfigure(index=0, weight=1)

        path_label: ctk.CTkLabel = ctk.CTkLabel(
            master=file_info_frame,
            text="Fichier généré :",
            text_color=DesignSystem.Color.GRAY,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.CAPTION,
            ),
            anchor="w",
        )
        path_label.grid(  # type: ignore
            row=0,
            column=0,
            padx=DesignSystem.Spacing.MD,
            pady=(DesignSystem.Spacing.MD, DesignSystem.Spacing.XS),
            sticky="ew",
        )

        file_path_display: ctk.CTkLabel = ctk.CTkLabel(
            master=file_info_frame,
            text=str(self._output_file_path.name),
            text_color=DesignSystem.Color.BLACK,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.BODY,
            ),
            anchor="w",
        )
        file_path_display.grid(  # type: ignore
            row=1,
            column=0,
            padx=DesignSystem.Spacing.MD,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.MD),
            sticky="ew",
        )

        button_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=inner_frame,
            fg_color=DesignSystem.Color.TRANSPARENT,
        )
        button_frame.grid(  # type: ignore
            row=3,
            column=0,
            sticky="ew",
        )
        button_frame.grid_columnconfigure(index=0, weight=1)
        button_frame.grid_columnconfigure(index=1, weight=1)

        open_button: ctk.CTkButton = ctk.CTkButton(
            master=button_frame,
            text="Ouvrir l'emplacement du fichier",
            command=self._open_output_file_location,
            height=DesignSystem.Height.SM,
            fg_color=DesignSystem.Color.PRIMARY,
            hover_color=DesignSystem.Color.DARKER_PRIMARY,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.BUTTON,
                weight="bold",
            ),
            text_color=DesignSystem.Color.WHITE,
            corner_radius=DesignSystem.Roundness.SM,
        )
        open_button.grid(  # type: ignore
            row=0,
            column=0,
            padx=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM),
            sticky="ew",
        )

        close_button: ctk.CTkButton = ctk.CTkButton(
            master=button_frame,
            text="Fermer",
            command=self._close,
            height=DesignSystem.Height.SM,
            fg_color=DesignSystem.Color.GRAY,
            hover_color=DesignSystem.Color.DARKER_GRAY,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.BUTTON,
            ),
            text_color=DesignSystem.Color.WHITE,
            corner_radius=DesignSystem.Roundness.SM,
        )
        close_button.grid(  # type: ignore
            row=0,
            column=1,
            padx=(DesignSystem.Spacing.SM, DesignSystem.Spacing.NONE),
            sticky="ew",
        )

    def _auto_size_window(self) -> None:

        self.update_idletasks()

        required_width: int = self.winfo_reqwidth()
        required_height: int = self.winfo_reqheight()

        padding: int = 20
        final_width: int = required_width + padding
        final_height: int = required_height + padding

        min_width: int = 450
        min_height: int = 250

        window_width: int = max(final_width, min_width)
        window_height: int = max(final_height, min_height)

        if self.master and hasattr(self.master, "winfo_x"):
            parent_x: int = self.master.winfo_x()
            parent_y: int = self.master.winfo_y()
            parent_width: int = self.master.winfo_width()
            parent_height: int = self.master.winfo_height()

            x: int = parent_x + (parent_width - window_width) // 2
            y: int = parent_y + (parent_height - window_height) // 2
        else:
            screen_width: int = self.winfo_screenwidth()
            screen_height: int = self.winfo_screenheight()
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def _open_output_file_location(self) -> None:

        try:
            system: str = platform.system()
            parent_dir: str = str(self._output_file_path.parent)

            if system == "Windows":
                subprocess.run(["explorer", parent_dir], check=True)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", parent_dir], check=True)
            else:  # Linux and other Unix-like systems
                subprocess.run(["xdg-open", parent_dir], check=True)
        except Exception:

            pass

    def _close(self) -> None:

        self.destroy()
