from __future__ import annotations

# Standard library imports
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.presentation.gui.styling.design_system import DesignSystem


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
            text="Le rapport a été généré avec succès !",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily,
                size=DesignSystem.FontSize.H1,
                weight="bold",
            ),
        )
        title_label.grid(row=0, column=0, padx=DesignSystem.Spacing.XL, pady=(DesignSystem.Spacing.XL, DesignSystem.Spacing.SM))  # type: ignore

        # Success message
        success_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self,
            text="Envoyez le report généré par email",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily, size=DesignSystem.FontSize.H2
            ),
            text_color=DesignSystem.Color.SUCCESS,
        )
        success_label.grid(row=1, column=0, padx=DesignSystem.Spacing.XL, pady=(DesignSystem.Spacing.SM, DesignSystem.Spacing.LG))  # type: ignore

        # File info frame - uses theme defaults
        file_frame: ctk.CTkFrame = ctk.CTkFrame(master=self)
        file_frame.grid(row=2, column=0, padx=DesignSystem.Spacing.XL, pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.LG), sticky="ew")  # type: ignore

        file_label: ctk.CTkLabel = ctk.CTkLabel(
            master=file_frame,
            text=f"Fichier : {self._file_path.split('/')[-1]}",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily, size=DesignSystem.FontSize.H3
            ),
            anchor="w",
        )
        file_label.grid(row=0, column=0, padx=DesignSystem.Spacing.MD, pady=DesignSystem.Spacing.SM, sticky="w")  # type: ignore

        # Email instruction
        instruction_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self,
            text="Veuillez saisir des adresses email (séparées par des virgules) :",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily, size=DesignSystem.FontSize.BODY
            ),
        )
        instruction_label.grid(row=3, column=0, padx=DesignSystem.Spacing.XL, pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.MD), sticky="w")  # type: ignore

        # Email entry
        self._email_entry: ctk.CTkEntry = ctk.CTkEntry(
            master=self,
            placeholder_text="example1@gmail.com, example2@gmail.com",
            height=40,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily, size=DesignSystem.FontSize.BODY
            ),
        )
        self._email_entry.grid(row=4, column=0, padx=DesignSystem.Spacing.XL, pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.LG), sticky="ew")  # type: ignore

        # Buttons frame
        buttons_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self, fg_color=DesignSystem.Color.TRANSPARENT
        )
        buttons_frame.grid(row=5, column=0, padx=DesignSystem.Spacing.XL, pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.XL))  # type: ignore

        # Cancel button - secondary style
        self._cancel_button: ctk.CTkButton = ctk.CTkButton(
            master=buttons_frame,
            text="Ignorer",
            command=self._close,
            width=100,
            height=35,
            fg_color=DesignSystem.Color.TRANSPARENT,
            border_width=1,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily, size=DesignSystem.FontSize.BUTTON
            ),
        )
        self._cancel_button.grid(row=0, column=0, padx=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM))  # type: ignore

        # Send button - primary style
        self._send_button: ctk.CTkButton = ctk.CTkButton(
            master=buttons_frame,
            text="Envoyer",
            command=self._send_email,
            width=120,
            height=35,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily,
                size=DesignSystem.FontSize.BUTTON,
                weight="bold",
            ),
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
        self._email_entry.configure(border_color=DesignSystem.Color.ERROR)  # type: ignore
        self.after(
            ms=2000,
            func=lambda: self._email_entry.configure(border_color=None),  # type: ignore
        )  # Reset to theme default

    def _close(self) -> None:
        self.grab_release()
        self.destroy()
