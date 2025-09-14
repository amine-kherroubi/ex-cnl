from __future__ import annotations

# Standard library imports
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore


class EmailDialog(ctk.CTkToplevel):
    __slots__ = (
        "_file_path",
        "_on_send",
        "_email_entry",
        "_send_button",
        "_cancel_button",
    )

    def __init__(
        self,
        parent: Any,
        file_path: str,
        on_send: Callable[[list[str], str], None],
    ) -> None:
        super().__init__(master=parent)  # type: ignore

        self._file_path: str = file_path
        self._on_send: Callable[[list[str], str], None] = on_send

        # Window configuration
        self.title(string="Envoyer par email")
        self.geometry(geometry_string="500x350")
        self.resizable(width=False, height=False)

        # Make modal
        self.transient(master=parent)  # type: ignore
        self.grab_set()

        self._setup_ui()

        # Focus on email entry
        self._email_entry.focus()

    def _setup_ui(self) -> None:
        # Configure grid
        self.grid_columnconfigure(index=0, weight=1)

        # Title
        title_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self,
            text="Envoyer le report généré",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title_label.grid(row=0, column=0, padx=30, pady=(30, 10))  # type: ignore

        # Success message
        success_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self,
            text="Le rapport a été généré avec succès !",
            font=ctk.CTkFont(size=14),
            text_color="green",
        )
        success_label.grid(row=1, column=0, padx=30, pady=(10, 20))  # type: ignore

        # File info
        file_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self,
            fg_color=("gray85", "gray25"),
            corner_radius=8,
        )
        file_frame.grid(row=2, column=0, padx=30, pady=(0, 20), sticky="ew")  # type: ignore

        file_label: ctk.CTkLabel = ctk.CTkLabel(
            master=file_frame,
            text=f"Fichier : {self._file_path.split('/')[-1]}",
            font=ctk.CTkFont(size=13),
            anchor="w",
        )
        file_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")  # type: ignore

        # Email instruction
        instruction_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self,
            text="Veuillez saisir des adresses email (séparées par des virgules) :",
            font=ctk.CTkFont(size=13),
        )
        instruction_label.grid(row=3, column=0, padx=30, pady=(0, 10), sticky="w")  # type: ignore

        # Email entry
        self._email_entry: ctk.CTkEntry = ctk.CTkEntry(
            master=self,
            placeholder_text="example1@gmail.com, example2@gmail.com",
            height=40,
            font=ctk.CTkFont(size=13),
        )
        self._email_entry.grid(row=4, column=0, padx=30, pady=(0, 20), sticky="ew")  # type: ignore

        # Buttons frame
        buttons_frame: ctk.CTkFrame = ctk.CTkFrame(master=self, fg_color="transparent")
        buttons_frame.grid(row=5, column=0, padx=30, pady=(0, 30))  # type: ignore

        # Cancel button
        self._cancel_button: ctk.CTkButton = ctk.CTkButton(
            master=buttons_frame,
            text="Ignorer",
            command=self._close,
            width=100,
            height=35,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray80", "gray30"),
            border_width=2,
            font=ctk.CTkFont(size=13),
        )
        self._cancel_button.grid(row=0, column=0, padx=(0, 10))  # type: ignore

        # Send button
        self._send_button: ctk.CTkButton = ctk.CTkButton(
            master=buttons_frame,
            text="Envoyer",
            command=self._send_email,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self._send_button.grid(row=0, column=1)  # type: ignore

        # Bind Enter key to send
        self._email_entry.bind(  # type: ignore
            sequence="<Return>", command=lambda event: self._send_email()  # type: ignore
        )

    def _send_email(self) -> None:
        email_text: str = self._email_entry.get().strip()  # type: ignore

        if not email_text:
            self._show_error(message="Veuillez saisir au moins une adresse email")
            return

        # Parse email addresses
        emails: list[str] = [email.strip() for email in email_text.split(",")]

        # Basic validation
        valid_emails: list[str] = []
        for email in emails:
            if "@" in email and "." in email:
                valid_emails.append(email)

        if not valid_emails:
            self._show_error(message="Veuillez saisir des adresses email valides")
            return

        # Call the callback
        self._on_send(valid_emails, self._file_path)

        # Close dialog
        self._close()

    def _show_error(self, message: str) -> None:
        # Flash the entry border red briefly
        self._email_entry.configure(border_color="red")  # type: ignore
        self.after(ms=2000, func=lambda: self._email_entry.configure(border_color=("gray70", "gray30")))  # type: ignore

        # You could also show a tooltip or label with the error message

    def _close(self) -> None:
        self.grab_release()
        self.destroy()
