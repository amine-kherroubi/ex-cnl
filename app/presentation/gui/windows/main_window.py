# Standard library imports
from logging import Logger
from typing import Any, Optional

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.core.domain.models.report_specification import ReportSpecification
from app.presentation.gui.styling.design_system import DesignSystem
from app.presentation.gui.views.menu_view import MenuView
from app.presentation.gui.views.report_views.factories.report_view_factory import (
    ReportViewFactory,
)
from app.presentation.gui.models.state import State
from app.core.facade import CoreFacade
from app.common.logging_setup import get_logger


class MainWindow(ctk.CTk):
    __slots__ = (
        "_logger",
        "_facade",
        "_state",
        "_current_view",
        "_container",
        "_title_label",
    )

    def __init__(self, core_facade: CoreFacade) -> None:
        super().__init__()  # type: ignore

        self._logger: Logger = get_logger(__name__)
        self._logger.info("Initializing main application window")

        self._facade: CoreFacade = core_facade
        self._state: State = State()
        self._current_view: Optional[ctk.CTkFrame] = None

        self.title("Générateur de rapports")
        self.geometry("800x600")
        self.resizable(False, False)
        ctk.set_widget_scaling(0.9)
        ctk.set_window_scaling(0.9)

        self._setup_ui()
        self._load_available_reports()
        self._show_menu()

        self._logger.info("Main application window initialized successfully")

    def _setup_ui(self) -> None:

        self.configure(fg_color=DesignSystem.Color.WHITE.value)  # type: ignore

        self.grid_columnconfigure(index=0, weight=1)
        self.grid_rowconfigure(index=1, weight=1)

        header_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self, fg_color=DesignSystem.Color.TRANSPARENT.value
        )
        header_frame.grid(  # type: ignore
            row=0,
            column=0,
            padx=DesignSystem.Spacing.XXL.value,
            pady=(DesignSystem.Spacing.XXL.value, DesignSystem.Spacing.LG.value),
            sticky="ew",
        )
        header_frame.grid_columnconfigure(index=0, weight=0)
        header_frame.grid_columnconfigure(index=1, weight=0)
        header_frame.grid_columnconfigure(index=2, weight=1)

        self._title: ctk.CTkLabel = ctk.CTkLabel(
            master=header_frame,
            text="Générateur de rapports",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value,
                size=DesignSystem.FontSize.H1.value,
                weight="bold",
            ),
            text_color=DesignSystem.Color.BLACK.value,
        )
        self._title.grid(row=0, column=0, sticky="w")  # type: ignore

        self._organization: ctk.CTkLabel = ctk.CTkLabel(
            master=header_frame,
            text="BNH (ex-CNL)",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value,
                size=DesignSystem.FontSize.H1.value,
                weight="normal",
                slant="italic",
            ),
            text_color=DesignSystem.Color.LIGHTER_GRAY.value,
        )
        self._organization.grid(row=0, column=1, padx=(DesignSystem.Spacing.SM.value, DesignSystem.Spacing.NONE.value), sticky="w")  # type: ignore

        self._container: ctk.CTkFrame = ctk.CTkFrame(
            master=self,
            fg_color=DesignSystem.Color.LEAST_WHITE.value,
            corner_radius=DesignSystem.Roundness.MD.value,
        )
        self._container.grid(row=1, column=0, padx=DesignSystem.Spacing.XXL.value, pady=(DesignSystem.Spacing.NONE.value, DesignSystem.Spacing.XXL.value), sticky="nsew")  # type: ignore
        self._container.grid_columnconfigure(index=0, weight=1)
        self._container.grid_rowconfigure(index=0, weight=1)

    def _load_available_reports(self) -> None:
        try:
            reports: dict[str, Any] = self._facade.get_available_reports()
            self._state.available_reports = reports
            self._logger.info(f"Loaded {len(reports)} report types")
        except Exception as e:
            self._logger.exception(f"Failed to load available reports: {e}")

    def _show_menu(self) -> None:
        self._clear_current_view()

        self._current_view = MenuView(
            parent=self._container,
            available_reports=self._state.available_reports,
            on_report_selected=self._show_report_view,
        )
        self._current_view.grid(row=0, column=0, sticky="nsew")  # type: ignore

    def _show_report_view(self, report_name: str) -> None:
        self._clear_current_view()
        report_spec: Optional[ReportSpecification] = self._state.available_reports.get(
            report_name
        )

        if not report_spec:
            self._logger.error(f"Report specification not found: {report_name}")
            return

        self._current_view = ReportViewFactory.create_view(
            parent=self._container,
            report_spec=report_spec,
            core_facade=self._facade,
            on_back=self._show_menu,
        )

        self._current_view.grid(row=0, column=0, sticky="nsew")  # type: ignore

    def _clear_current_view(self) -> None:
        if self._current_view:
            self._current_view.destroy()
            self._current_view = None
