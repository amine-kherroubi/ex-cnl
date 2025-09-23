from __future__ import annotations

# Standard library imports
from datetime import datetime
from typing import Any, Literal, TypeAlias

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.presentation.gui.components.base_component import BaseComponent
from app.presentation.gui.styling.design_system import DesignSystem

MessageType: TypeAlias = Literal["information", "succès", "avertissement", "erreur"]


class StatusDisplay(BaseComponent):
    """Component for displaying status messages and progress information."""

    __slots__ = ("_status_text",)

    def __init__(self, parent: Any) -> None:
        super().__init__(parent, "Statut")

    def _setup_content(self) -> None:
        """Set up the status display content."""
        # Configure grid
        self._content_frame.grid_columnconfigure(index=0, weight=1)
        self._content_frame.grid_rowconfigure(index=1, weight=1)

        # Title
        title: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text=self._title,
            text_color=DesignSystem.Color.BLACK,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.H3,
                weight="bold",
            ),
            anchor="w",
        )
        title.grid(  # type: ignore
            row=0,
            column=0,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM),
            sticky="w",
        )

        # Information text
        information: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text="Les messages de progression et d'erreur apparaîtront ici",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.CAPTION,
            ),
            text_color=DesignSystem.Color.GRAY,
        )
        information.grid(  # type: ignore
            row=1,
            column=0,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM),
            sticky="w",
        )

        # Status text area
        self._status_text: ctk.CTkTextbox = ctk.CTkTextbox(
            master=self._content_frame,
            state="disabled",
            border_width=DesignSystem.BorderWidth.XS,
            corner_radius=DesignSystem.Roundness.SM,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.MONO,
                size=DesignSystem.FontSize.CAPTION,
            ),
        )
        self._status_text.grid(  # type: ignore
            row=2,
            column=0,
            sticky="nsew",
        )

        # Initialize with welcome message
        self.add_message(
            message="Veuillez insérer les fichiers nécessaires pour générer le rapport",
            message_type="information",
        )

    def add_message(
        self, message: str, message_type: MessageType = "information"
    ) -> None:
        """Add a message to the status display with timestamp and type indicator."""
        timestamp: str = datetime.now().strftime("%H:%M:%S")

        indications_map: dict[MessageType, str] = {
            "information": DesignSystem.Color.INFO,
            "succès": DesignSystem.Color.SUCCESS,
            "avertissement": DesignSystem.Color.WARNING,
            "erreur": DesignSystem.Color.ERROR,
        }

        color: str = indications_map.get(message_type, DesignSystem.Color.INFO)
        formatted_message: str = f"[{timestamp}] {message}\n"

        # Add message to text area
        self._status_text.configure(state="normal")  # type: ignore
        self._status_text.insert("end", formatted_message, message_type)  # type: ignore
        self._status_text.tag_config(message_type, foreground=color)  # type: ignore
        self._status_text.see("end")  # type: ignore
        self._status_text.configure(state="disabled")  # type: ignore

    def clear_messages(self) -> None:
        """Clear all messages from the status display."""
        self._status_text.configure(state="normal")  # type: ignore
        self._status_text.delete(index1="1.0", index2="end")  # type: ignore
        self._status_text.configure(state="disabled")  # type: ignore
