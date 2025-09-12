from __future__ import annotations

# Standard library imports
from typing import Any

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from gui.views.menu_view import MenuView
from gui.views.document_view import DocumentView
from gui.views.settings_view import SettingsView
from gui.models.gui_state import GUIState
from gui.controllers.document_controller import DocumentController


class MainWindow(ctk.CTk):
    __slots__ = (
        "_state",
        "_controller",
        "_current_view",
        "_container",
        "_title_label",
    )

    def __init__(self) -> None:
        super().__init__()  # type: ignore

        # Window configuration
        self.title(string="Document Generator")
        self.geometry(geometry_string="900x700")
        self.minsize(width=700, height=600)

        # Set theme
        ctk.set_appearance_mode(mode_string="system")
        ctk.set_default_color_theme(color_string="green")

        # Initialize state and controller
        self._state: GUIState = GUIState()
        self._controller: DocumentController = DocumentController()
        self._current_view: ctk.CTkFrame | None = None

        # Setup UI
        self._setup_ui()

        # Load available reports and show menu
        self._load_available_reports()
        self._show_menu()

    def _setup_ui(self) -> None:
        # Configure grid weights
        self.grid_columnconfigure(index=0, weight=1)
        self.grid_rowconfigure(index=1, weight=1)

        # Title
        self._title_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self,
            text="Document Generator",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        self._title_label.grid(row=0, column=0, padx=30, pady=(30, 20), sticky="w")  # type: ignore

        # Main container for views
        self._container: ctk.CTkFrame = ctk.CTkFrame(master=self)
        self._container.grid(row=1, column=0, padx=30, pady=(0, 30), sticky="nsew")  # type: ignore
        self._container.grid_columnconfigure(index=0, weight=1)
        self._container.grid_rowconfigure(index=0, weight=1)

    def _load_available_reports(self) -> None:
        try:
            reports: dict[str, Any] = self._controller.get_available_reports()
            self._state.available_reports = reports
        except Exception as e:
            print(f"Error loading reports: {str(e)}")

    def _show_menu(self) -> None:
        self._clear_current_view()
        self._title_label.configure(text="Document Generator")  # type: ignore

        self._current_view = MenuView(
            parent=self._container,
            available_documents=self._state.available_reports,
            on_document_selected=self._show_document_view,
            on_settings_selected=self._show_settings_view,
        )
        self._current_view.grid(row=0, column=0, sticky="nsew")  # type: ignore

    def _show_document_view(self, document_name: str) -> None:
        self._clear_current_view()
        self._title_label.configure(text=f"Generate: {document_name}")  # type: ignore

        document_spec: Any = self._state.available_reports.get(document_name)

        self._current_view = DocumentView(
            parent=self._container,
            document_name=document_name,
            document_spec=document_spec,
            controller=self._controller,
            on_back=self._show_menu,
        )
        self._current_view.grid(row=0, column=0, sticky="nsew")  # type: ignore

    def _show_settings_view(self, document_name: str) -> None:
        self._clear_current_view()
        self._title_label.configure(text=f"Settings: {document_name}")  # type: ignore

        self._current_view = SettingsView(
            parent=self._container,
            document_name=document_name,
            on_back=self._show_menu,
        )
        self._current_view.grid(row=0, column=0, sticky="nsew")  # type: ignore

    def _clear_current_view(self) -> None:
        if self._current_view:
            self._current_view.destroy()
            self._current_view = None


def main() -> None:
    app: MainWindow = MainWindow()
    app.mainloop()  # type: ignore


if __name__ == "__main__":
    main()
