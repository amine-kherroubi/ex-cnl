from __future__ import annotations

# Standard library imports
from logging import Logger
from pathlib import Path
from typing import Any

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.core.domain.models.report_specification import ReportSpecification
from app.presentation.gui.views.menu_view import MenuView
from app.presentation.gui.views.report_views.report_view_factory import (
    ReportViewFactory,
)
from app.presentation.gui.views.settings_view import SettingsView
from app.presentation.gui.models.gui_state import GUIState
from app.presentation.gui.controllers.report_controller import ReportController
from app.core.core_facade import CoreFacade
from app.core.utils.logging_setup import get_logger


class MainWindow(ctk.CTk):
    __slots__ = (
        "_logger",
        "_facade",
        "_state",
        "_controller",
        "_current_view",
        "_container",
        "_title_label",
    )

    def __init__(self, facade: CoreFacade) -> None:
        super().__init__()  # type: ignore

        self._logger: Logger = get_logger(__name__)
        self._logger.info("Initializing main application window")

        self._state: GUIState = GUIState()
        self._controller: ReportController = ReportController(facade)
        self._current_view: ctk.CTkFrame | None = None

        # Window configuration
        self.title(string="Générateur de rapports")
        self.geometry(geometry_string="900x700")
        self.minsize(width=700, height=600)

        # Set theme
        ctk.set_appearance_mode(mode_string="light")
        theme_path: Path = Path(__file__).parent / "styling/theme.json"
        if theme_path.exists():
            ctk.set_default_color_theme(str(theme_path))
        else:
            self._logger.warning(
                f"Theme file not found at {theme_path}, using default theme"
            )
            ctk.set_default_color_theme("blue")

        # Scaling - modern and appropriate for high-DPI displays
        ctk.set_widget_scaling(1.0)
        ctk.set_window_scaling(1.0)

        # Setup UI
        self._setup_ui()
        self._load_available_reports()
        self._show_menu()

        self._logger.info("Main application window initialized successfully")

    def _setup_ui(self) -> None:
        # Configure grid weights
        self.grid_columnconfigure(index=0, weight=1)
        self.grid_rowconfigure(index=1, weight=1)

        # Header frame
        header_frame: ctk.CTkFrame = ctk.CTkFrame(master=self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=30, pady=(30, 20), sticky="ew")  # type: ignore
        header_frame.grid_columnconfigure(index=0, weight=1)

        # Title - using modern typography
        self._title_label: ctk.CTkLabel = ctk.CTkLabel(
            master=header_frame,
            text="Générateur de rapports",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self._title_label.grid(row=0, column=0, sticky="w")  # type: ignore

        # Main container for views
        self._container: ctk.CTkFrame = ctk.CTkFrame(master=self)
        self._container.grid(row=1, column=0, padx=30, pady=(0, 30), sticky="nsew")  # type: ignore
        self._container.grid_columnconfigure(index=0, weight=1)
        self._container.grid_rowconfigure(index=0, weight=1)

    def _load_available_reports(self) -> None:
        try:
            reports: dict[str, Any] = self._controller.get_available_reports()
            self._state.available_reports = reports
            self._logger.info(f"Loaded {len(reports)} report types")
        except Exception as e:
            self._logger.exception(f"Failed to load available reports: {e}")

    def _show_menu(self) -> None:
        self._clear_current_view()
        self._title_label.configure(text="Générateur de rapports")  # type: ignore

        self._current_view = MenuView(
            parent=self._container,
            available_reports=self._state.available_reports,
            on_report_selected=self._show_report_view,
            on_settings_selected=self._show_settings_view,
        )
        self._current_view.grid(row=0, column=0, sticky="nsew")  # type: ignore

    def _show_report_view(self, report_name: str) -> None:
        self._clear_current_view()
        report_spec: ReportSpecification | None = self._state.available_reports.get(
            report_name
        )

        if not report_spec:
            self._logger.error(f"Report specification not found: {report_name}")
            return

        self._title_label.configure(text=f"Générer : {report_spec.display_name}")  # type: ignore

        self._current_view = ReportViewFactory.create_view(
            parent=self._container,
            report_spec=report_spec,
            controller=self._controller,
            on_back=self._show_menu,
        )

        self._current_view.grid(row=0, column=0, sticky="nsew")  # type: ignore

    def _show_settings_view(self, report_name: str) -> None:
        self._clear_current_view()
        self._title_label.configure(text=f"Configuration : {report_name}")  # type: ignore

        self._current_view = SettingsView(
            parent=self._container,
            report_name=report_name,
            on_back=self._show_menu,
        )
        self._current_view.grid(row=0, column=0, sticky="nsew")  # type: ignore

    def _clear_current_view(self) -> None:
        if self._current_view:
            self._current_view.destroy()
            self._current_view = None
