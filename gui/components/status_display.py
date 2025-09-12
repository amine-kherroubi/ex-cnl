from __future__ import annotations

# Standard library imports
from datetime import datetime
from typing import Any, Literal


# Third-party imports
import customtkinter as ctk


MessageType = Literal["info", "success", "warning", "error"]


class StatusDisplay(ctk.CTkFrame):
    """Component for displaying status messages."""

    def __init__(self, parent: Any) -> None:
        super().__init__(parent)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Label
        label = ctk.CTkLabel(
            self, text="Status:", font=ctk.CTkFont(size=14, weight="bold")
        )
        label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # Status text area
        self._status_text = ctk.CTkTextbox(self, state="disabled")
        self._status_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # Initialize with welcome message
        self.add_message("Ready to generate documents", "info")

    def add_message(self, message: str, message_type: MessageType = "info") -> None:
        """Add a status message."""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Choose emoji based on message type
        emoji_map = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
        emoji = emoji_map.get(message_type, "ℹ️")

        formatted_message = f"[{timestamp}] {emoji} {message}\n"

        # Add message to text area
        self._status_text.configure(state="normal")
        self._status_text.insert("end", formatted_message)
        self._status_text.see("end")  # Scroll to bottom
        self._status_text.configure(state="disabled")

    def clear_messages(self) -> None:
        """Clear all status messages."""
        self._status_text.configure(state="normal")
        self._status_text.delete("1.0", "end")
        self._status_text.configure(state="disabled")
