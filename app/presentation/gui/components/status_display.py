from __future__ import annotations

# Standard library imports
from datetime import datetime
from typing import Any, Literal, TypeAlias

# Third-party imports
import customtkinter as ctk  # type: ignore

MessageType: TypeAlias = Literal["information", "succès", "avertissement", "erreur"]


class StatusDisplay(ctk.CTkFrame):
    __slots__ = ("_status_text",)

    def __init__(self, parent: Any) -> None:
        super().__init__(master=parent)  # type: ignore

        self._setup_ui()

    def _setup_ui(self) -> None:
        # Configure grid
        self.grid_columnconfigure(index=0, weight=1)
        self.grid_rowconfigure(index=1, weight=1)

        # Label
        label: ctk.CTkLabel = ctk.CTkLabel(
            master=self, text="Statut :", font=ctk.CTkFont(size=14, weight="bold")
        )
        label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")  # type: ignore

        # Status text area
        self._status_text: ctk.CTkTextbox = ctk.CTkTextbox(
            master=self, state="disabled"
        )
        self._status_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")  # type: ignore

        # Initialize with welcome message
        self.add_message(
            message="Prêt à générer un rapport", message_type="information"
        )

    def add_message(
        self, message: str, message_type: MessageType = "information"
    ) -> None:
        timestamp: str = datetime.now().strftime("%H:%M:%S")

        # Choose prefix based on message type
        prefix_map: dict[MessageType, str] = {
            "information": "[INFORMATION]",
            "succès": "[SUCCÈS]",
            "avertissement": "[AVERTISSEMENT]",
            "erreur": "[ERREUR]",
        }
        prefix: str = prefix_map.get(message_type, "[INFO]")

        formatted_message: str = f"[{timestamp}] {prefix} {message}\n"

        # Add message to text area
        self._status_text.configure(state="normal")  # type: ignore
        self._status_text.insert(index="end", text=formatted_message)  # type: ignore
        self._status_text.see(index="end")  # type: ignore # Scroll to bottom
        self._status_text.configure(state="disabled")  # type: ignore

    def clear_messages(self) -> None:
        self._status_text.configure(state="normal")  # type: ignore
        self._status_text.delete(index1="1.0", index2="end")  # type: ignore
        self._status_text.configure(state="disabled")  # type: ignore
