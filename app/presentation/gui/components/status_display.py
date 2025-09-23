from __future__ import annotations

# Standard library imports
from datetime import datetime
from typing import Any, Literal, TypeAlias

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.presentation.gui.styling.design_system import DesignSystem

MessageType: TypeAlias = Literal["information", "succès", "avertissement", "erreur"]


class StatusDisplay(ctk.CTkFrame):
    __slots__ = ("_status_text",)

    def __init__(self, parent: Any) -> None:
        super().__init__(master=parent)  # type: ignore

        self._setup_ui()

    def _setup_ui(self) -> None:
        # Self configuration
        self.configure(  # type: ignore
            fg_color=DesignSystem.Color.WHITE,
            corner_radius=DesignSystem.Roundness.MD,
        )

        # Configure grid
        self.grid_columnconfigure(index=0, weight=1)
        self.grid_rowconfigure(index=1, weight=1)

        # Label
        label: ctk.CTkLabel = ctk.CTkLabel(
            master=self,
            text="Statut",
            font=ctk.CTkFont(size=DesignSystem.FontSize.H3, weight="bold"),
        )
        label.grid(row=0, column=0, padx=DesignSystem.Spacing.SM, pady=DesignSystem.Spacing.XS, sticky="w")  # type: ignore

        # Status text area
        self._status_text: ctk.CTkTextbox = ctk.CTkTextbox(
            master=self, state="disabled"
        )
        self._status_text.grid(row=1, column=0, padx=DesignSystem.Spacing.SM, pady=DesignSystem.Spacing.SM, sticky="nsew")  # type: ignore

        # Information text
        information: ctk.CTkLabel = ctk.CTkLabel(
            master=self,
            text="Les messages de progression et d’erreur apparaîtront ici",
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

        # Initialize with welcome message
        self.add_message(
            message="Prêt à générer le rapport", message_type="information"
        )

    def add_message(
        self, message: str, message_type: MessageType = "information"
    ) -> None:
        timestamp: str = datetime.now().strftime("%H:%M:%S")

        indications_map: dict[MessageType, tuple[str, str]] = {
            "information": ("[INFO]", DesignSystem.Color.INFO),
            "succès": ("[SUCCÈS]", DesignSystem.Color.SUCCESS),
            "avertissement": ("[AVERTISSEMENT]", DesignSystem.Color.WARNING),
            "erreur": ("[ERREUR]", DesignSystem.Color.ERROR),
        }

        prefix: str = indications_map.get(
            message_type, ("[INFO]", DesignSystem.Color.INFO)
        )[0]
        color: str = indications_map.get(
            message_type, ("[INFO]", DesignSystem.Color.INFO)
        )[1]
        formatted_message: str = f"[{timestamp}] {prefix} {message}\n"

        # Add message to text area
        self._status_text.configure(state="normal")  # type: ignore
        self._status_text.insert("end", formatted_message, message_type)  # type: ignore
        self._status_text.tag_config(message_type, foreground=color)  # type: ignore
        self._status_text.see("end")  # type: ignore
        self._status_text.configure(state="disabled")  # type: ignore

    def clear_messages(self) -> None:
        self._status_text.configure(state="normal")  # type: ignore
        self._status_text.delete(index1="1.0", index2="end")  # type: ignore
        self._status_text.configure(state="disabled")  # type: ignore
