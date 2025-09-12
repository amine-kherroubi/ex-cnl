from __future__ import annotations

# Standard library imports
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore


class DocumentCard(ctk.CTkFrame):
    __slots__ = (
        "_document_name",
        "_document_spec",
        "_on_generate_clicked",
        "_on_settings_clicked",
        "_generate_button",
        "_settings_button",
    )

    def __init__(
        self,
        parent: Any,
        document_name: str,
        document_spec: Any,
        on_generate_clicked: Callable[[], None],
        on_settings_clicked: Callable[[], None],
    ) -> None:
        super().__init__(master=parent)  # type: ignore

        self._document_name: str = document_name
        self._document_spec: Any = document_spec
        self._on_generate_clicked: Callable[[], None] = on_generate_clicked
        self._on_settings_clicked: Callable[[], None] = on_settings_clicked

        self._setup_ui()

    def _setup_ui(self) -> None:
        # Configure grid
        self.grid_columnconfigure(index=0, weight=1)

        # Card styling
        self.configure(fg_color=("gray90", "gray20"))  # type: ignore

        # Content frame
        content_frame: ctk.CTkFrame = ctk.CTkFrame(master=self, fg_color="transparent")
        content_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")  # type: ignore
        content_frame.grid_columnconfigure(index=0, weight=1)

        # Document info
        info_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=content_frame, fg_color="transparent"
        )
        info_frame.grid(row=0, column=0, sticky="ew")  # type: ignore
        info_frame.grid_columnconfigure(index=0, weight=1)

        # Extract document info
        display_name: str = getattr(
            self._document_spec, "display_name", self._document_name
        )
        description: str = getattr(
            self._document_spec, "description", "No description available"
        )
        category: str = getattr(self._document_spec, "category", "Unknown")
        periodicity: str = getattr(self._document_spec, "periodicity", "Unknown")

        # Title
        title_label: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text=f"📊 {display_name}",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        )
        title_label.grid(row=0, column=0, sticky="w")  # type: ignore

        # Category and periodicity
        meta_label: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text=f"📁 {category} • ⏰ {periodicity}",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60"),
            anchor="w",
        )
        meta_label.grid(row=1, column=0, pady=(5, 10), sticky="w")  # type: ignore

        # Description
        desc_label: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text=description,
            font=ctk.CTkFont(size=14),
            anchor="w",
            wraplength=500,
            justify="left",
        )
        desc_label.grid(row=2, column=0, pady=(0, 15), sticky="w")  # type: ignore

        # Buttons frame
        buttons_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=content_frame, fg_color="transparent"
        )
        buttons_frame.grid(row=1, column=0, sticky="ew")  # type: ignore
        buttons_frame.grid_columnconfigure(index=0, weight=1)

        # Generate button
        self._generate_button: ctk.CTkButton = ctk.CTkButton(
            master=buttons_frame,
            text="Generate Document",
            command=self._on_generate_clicked,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self._generate_button.grid(row=0, column=0, padx=(0, 10), sticky="ew")  # type: ignore

        # Settings button
        self._settings_button: ctk.CTkButton = ctk.CTkButton(
            master=buttons_frame,
            text="⚙️ Settings",
            command=self._on_settings_clicked,
            width=100,
            height=35,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray80", "gray30"),
            border_width=2,
            font=ctk.CTkFont(size=14),
        )
        self._settings_button.grid(row=0, column=1, sticky="e")  # type: ignore
