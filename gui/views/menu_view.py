from __future__ import annotations

# Standard library imports
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from gui.components.document_card import DocumentCard


class MenuView(ctk.CTkFrame):
    __slots__ = (
        "_available_documents",
        "_on_document_selected",
        "_on_settings_selected",
        "_document_cards",
    )

    def __init__(
        self,
        parent: Any,
        available_documents: dict[str, Any],
        on_document_selected: Callable[[str], None],
        on_settings_selected: Callable[[str], None],
    ) -> None:
        super().__init__(master=parent)  # type: ignore

        self._available_documents: dict[str, Any] = available_documents
        self._on_document_selected: Callable[[str], None] = on_document_selected
        self._on_settings_selected: Callable[[str], None] = on_settings_selected
        self._document_cards: list[DocumentCard] = []

        self._setup_ui()

    def _setup_ui(self) -> None:
        # Configure grid
        self.grid_columnconfigure(index=0, weight=1)

        # Header
        header_frame: ctk.CTkFrame = ctk.CTkFrame(master=self)
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")  # type: ignore
        header_frame.grid_columnconfigure(index=0, weight=1)

        header_label: ctk.CTkLabel = ctk.CTkLabel(
            master=header_frame,
            text="Sélectionner le type de document",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        header_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")  # type: ignore

        description_label: ctk.CTkLabel = ctk.CTkLabel(
            master=header_frame,
            text="Choisissez un type de document à générer ou configurez ses paramètres",
            font=ctk.CTkFont(size=14),
            text_color=("gray30", "gray70"),
        )
        description_label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")  # type: ignore

        # Scrollable frame for document cards
        scrollable_frame: ctk.CTkScrollableFrame = ctk.CTkScrollableFrame(master=self)
        scrollable_frame.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="nsew")  # type: ignore
        scrollable_frame.grid_columnconfigure(index=0, weight=1)
        self.grid_rowconfigure(index=1, weight=1)

        # Create document cards
        for idx, (doc_name, doc_spec) in enumerate(self._available_documents.items()):
            card: DocumentCard = DocumentCard(
                parent=scrollable_frame,
                document_spec=doc_spec,
                on_generate_clicked=lambda name=doc_name: self._on_document_selected(
                    name
                ),
                on_settings_clicked=lambda name=doc_name: self._on_settings_selected(
                    name
                ),
            )
            card.grid(row=idx, column=0, padx=10, pady=10, sticky="ew")  # type: ignore
            self._document_cards.append(card)
