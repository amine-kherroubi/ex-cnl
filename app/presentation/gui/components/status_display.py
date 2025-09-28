# Standard library imports
from datetime import datetime
from typing import Any, Literal

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.presentation.gui.components.base_component import BaseComponent
from app.presentation.gui.styling.design_system import DesignSystem

MessageType = Literal["information", "succès", "avertissement", "erreur"]


class StatusDisplay(BaseComponent):
    __slots__ = ("_status_text",)

    def __init__(self, parent: Any) -> None:
        super().__init__(parent, "Statut")

    def _setup_content(self) -> None:

        self._content_frame.grid_columnconfigure(index=0, weight=1)
        self._content_frame.grid_rowconfigure(index=1, weight=1)

        title: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text=self._title,
            text_color=DesignSystem.Color.BLACK.value,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value,
                size=DesignSystem.FontSize.H3.value,
                weight="bold",
            ),
            anchor="w",
        )
        title.grid(  # type: ignore
            row=0,
            column=0,
            pady=(DesignSystem.Spacing.NONE.value, DesignSystem.Spacing.SM.value),
            sticky="w",
        )

        information: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text="Les messages de progression et d'erreur apparaîtront ici",
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

        self._status_text: ctk.CTkTextbox = ctk.CTkTextbox(
            master=self._content_frame,
            state="disabled",
            border_width=DesignSystem.BorderWidth.XS.value,
            corner_radius=DesignSystem.Roundness.SM.value,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.MONO.value, size=DesignSystem.FontSize.CAPTION.value
            ),
            fg_color=DesignSystem.Color.LEAST_WHITE.value,
            border_color=DesignSystem.Color.LIGHTER_GRAY.value,
        )
        self._status_text.grid(  # type: ignore
            row=2,
            column=0,
            sticky="nsew",
        )

        self.add_message(
            message="Veuillez insérer les fichiers nécessaires pour générer le rapport",
            message_type="information",
        )

    def add_message(
        self, message: str, message_type: MessageType = "information"
    ) -> None:

        timestamp: str = datetime.now().strftime("%H:%M:%S")

        indications_map: dict[MessageType, str] = {
            "information": DesignSystem.Color.INFO.value,
            "succès": DesignSystem.Color.SUCCESS.value,
            "avertissement": DesignSystem.Color.WARNING.value,
            "erreur": DesignSystem.Color.ERROR.value,
        }

        color: str = indications_map.get(message_type, DesignSystem.Color.INFO.value)
        formatted_message: str = f"[{timestamp}] {message}\n"

        self._status_text.configure(state="normal")  # type: ignore
        self._status_text.insert("end", formatted_message, message_type)  # type: ignore
        self._status_text.tag_config(message_type, foreground=color)  # type: ignore
        self._status_text.see("end")  # type: ignore
        self._status_text.configure(state="disabled")  # type: ignore

    def clear_messages(self) -> None:

        self._status_text.configure(state="normal")  # type: ignore
        self._status_text.delete(index1="1.0", index2="end")  # type: ignore
        self._status_text.configure(state="disabled")  # type: ignore
