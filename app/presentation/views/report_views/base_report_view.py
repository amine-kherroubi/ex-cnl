from __future__ import annotations

# Standard library imports
from abc import abstractmethod
import threading
from pathlib import Path
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.core.domain.enums.space_time import Month
from app.core.domain.models.report_specification import ReportSpecification
from app.presentation.components.date_selector import DateSelector
from app.presentation.components.file_selector import FileSelector
from app.presentation.components.output_selector import OutputSelector
from app.presentation.components.status_display import StatusDisplay
from app.presentation.components.required_files import RequiredFilesComponent
from app.presentation.windows.success_window import SuccessWindow
from app.presentation.controllers.report_controller import ReportController
from app.presentation.styling.design_system import DesignSystem


class BaseReportView(ctk.CTkFrame):
    __slots__ = (
        "_report_spec",
        "_controller",
        "_on_back",
        "_date_selector",
        "_file_selector",
        "_output_selector",
        "_status_display",
        "_required_files_component",
        "_generate_button",
        "_back_button",
        "_selected_month",
        "_selected_year",
        "_selected_files",
        "_output_path",
        "_last_generated_file",
        "_scrollable_frame",
        "_next_row",
    )

    def __init__(
        self,
        parent: Any,
        report_spec: ReportSpecification,
        controller: ReportController,
        on_back: Callable[[], None],
    ) -> None:
        super().__init__(master=parent)  # type: ignore
        self._report_spec: ReportSpecification = report_spec
        self._controller: ReportController = controller
        self._on_back: Callable[[], None] = on_back
        self._selected_month: Month | None = None
        self._selected_year: int | None = None
        self._selected_files: list[Path] = []
        self._output_path: Path | None = None
        self._last_generated_file: Path | None = None
        self._next_row: int = 0

        self._setup_ui()

    def _setup_ui(self) -> None:
        self.configure(  # type: ignore
            fg_color=DesignSystem.Color.LEAST_WHITE,
            border_color=DesignSystem.Color.LIGHTER_GRAY,
            corner_radius=DesignSystem.Roundness.MD,
            border_width=DesignSystem.BorderWidth.XS,
        )

        self.grid_columnconfigure(index=0, weight=1)
        self.grid_rowconfigure(index=1, weight=1)

        self._setup_header()

        self._scrollable_frame = ctk.CTkScrollableFrame(
            master=self,
            fg_color=DesignSystem.Color.TRANSPARENT,
        )
        self._scrollable_frame.grid(row=1, column=0, padx=DesignSystem.Spacing.XS, pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.LG), sticky="nsew")  # type: ignore
        self._scrollable_frame.grid_columnconfigure(index=0, weight=1)

        self._setup_report_specific_components()

        self._setup_common_components()

        self._setup_action_buttons()

        self._selected_month = self._date_selector.get_selected_month()
        self._selected_year = self._date_selector.get_selected_year()
        self._update_generate_button_state()

    def _setup_header(self) -> None:
        header_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self, fg_color=DesignSystem.Color.TRANSPARENT
        )
        header_frame.grid(row=0, column=0, padx=DesignSystem.Spacing.LG, pady=(DesignSystem.Spacing.LG, DesignSystem.Spacing.XS), sticky="ew")  # type: ignore
        header_frame.grid_columnconfigure(index=1, weight=1)

        self._back_button = ctk.CTkButton(
            master=header_frame,
            text="Retour",
            text_color=DesignSystem.Color.WHITE,
            fg_color=DesignSystem.Color.GRAY,
            hover_color=DesignSystem.Color.DARKER_GRAY,
            corner_radius=DesignSystem.Roundness.XS,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.BUTTON,
                weight="bold",
            ),
            command=self._on_back,
            width=DesignSystem.Width.SM,
            height=DesignSystem.Height.SM,
        )
        self._back_button.grid(row=0, column=0, padx=DesignSystem.Spacing.NONE, sticky="w")  # type: ignore

        info_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=header_frame, fg_color=DesignSystem.Color.TRANSPARENT
        )
        info_frame.grid(row=0, column=1, sticky="ew")  # type: ignore
        info_frame.grid_columnconfigure(index=0, weight=1)

        title_label: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text=self._report_spec.display_name,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.H2,
                weight="bold",
            ),
            text_color=DesignSystem.Color.BLACK,
        )
        title_label.grid(row=0, column=0, padx=DesignSystem.Spacing.MD, pady=DesignSystem.Spacing.XS, sticky="w")  # type: ignore

    def _setup_common_components(self) -> None:
        self._date_selector = DateSelector(
            parent=self._scrollable_frame, on_date_changed=self._on_date_changed
        )
        self._date_selector.grid(row=self._next_row, column=0, padx=DesignSystem.Spacing.SM, pady=DesignSystem.Spacing.SM, sticky="ew")  # type: ignore
        self._next_row += 1

        self._required_files_component = RequiredFilesComponent(
            parent=self._scrollable_frame,
            report_spec=self._report_spec,
        )
        self._required_files_component.grid(row=self._next_row, column=0, padx=DesignSystem.Spacing.SM, pady=DesignSystem.Spacing.SM, sticky="ew")  # type: ignore
        self._next_row += 1

        self._file_selector = FileSelector(
            parent=self._scrollable_frame, on_files_changed=self._on_files_changed
        )
        self._file_selector.grid(row=self._next_row, column=0, padx=DesignSystem.Spacing.SM, pady=DesignSystem.Spacing.SM, sticky="ew")  # type: ignore
        self._next_row += 1

        self._output_selector = OutputSelector(
            parent=self._scrollable_frame, on_output_changed=self._on_output_changed
        )
        self._output_selector.grid(row=self._next_row, column=0, padx=DesignSystem.Spacing.SM, pady=DesignSystem.Spacing.SM, sticky="ew")  # type: ignore
        self._next_row += 1

    @abstractmethod
    def _setup_report_specific_components(self) -> None: ...

    def _setup_action_buttons(self) -> None:
        self._status_display = StatusDisplay(parent=self._scrollable_frame)
        self._status_display.grid(row=self._next_row, column=0, padx=DesignSystem.Spacing.SM, pady=DesignSystem.Spacing.SM, sticky="ew")  # type: ignore
        self._next_row += 1

        button_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self._scrollable_frame,
            fg_color=DesignSystem.Color.TRANSPARENT,
        )
        button_frame.grid(row=self._next_row, column=0, padx=DesignSystem.Spacing.SM, pady=DesignSystem.Spacing.SM, sticky="ew")  # type: ignore
        button_frame.grid_columnconfigure(index=0, weight=1)

        self._generate_button = ctk.CTkButton(
            master=button_frame,
            text="Générer le rapport",
            text_color=DesignSystem.Color.GRAY,
            fg_color=DesignSystem.Color.LESS_WHITE,
            hover_color=DesignSystem.Color.LEAST_WHITE,
            corner_radius=DesignSystem.Roundness.SM,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.BUTTON,
                weight="bold",
            ),
            command=self._generate_report,
            height=40,
        )
        self._generate_button.grid(row=0, column=0, sticky="ew")  # type: ignore
        self._generate_button.configure(state="disabled")  # type: ignore

    def _on_date_changed(self, month: Month | None, year: int | None) -> None:
        self._selected_month = month
        self._selected_year = year
        self._update_generate_button_state()

        if month and year:
            self._status_display.add_message(
                message=f"Période sélectionnée : {month.capitalize()} {year}",
                message_type="information",
            )

    def _on_files_changed(self, files: list[Path]) -> None:
        self._selected_files = files
        self._update_generate_button_state()

        if files:
            self._status_display.add_message(
                message=f"{len(files)} fichier(s) sélectionné(s)",
                message_type="information",
            )
        else:
            self._status_display.add_message(
                message="Aucun fichier sélectionné", message_type="avertissement"
            )

    def _on_output_changed(self, output_path: Path | None) -> None:
        self._output_path = output_path
        self._update_generate_button_state()

        if output_path:
            self._status_display.add_message(
                message=f"Répertoire de destination : {output_path}",
                message_type="information",
            )
        else:
            self._status_display.add_message(
                message="Aucun répertoire de destination sélectionné",
                message_type="avertissement",
            )

    def _can_generate(self) -> bool:
        return (
            len(self._selected_files) > 0
            and self._output_path is not None
            and self._selected_month is not None
            and self._selected_year is not None
        )

    def _update_generate_button_state(self) -> None:
        if not hasattr(self, "_generate_button"):
            return

        if self._can_generate():
            self._generate_button.configure(  # type: ignore
                state="normal",
                text_color=DesignSystem.Color.WHITE,
                fg_color=DesignSystem.Color.PRIMARY,
                hover_color=DesignSystem.Color.DARKER_PRIMARY,
            )
        else:
            self._generate_button.configure(  # type: ignore
                state="disabled",
                text_color=DesignSystem.Color.GRAY,
                fg_color=DesignSystem.Color.LESS_WHITE,
                hover_color=DesignSystem.Color.LEAST_WHITE,
            )

    def _get_generation_parameters(self) -> dict[str, Any]:
        return {}

    def _generate_report(self) -> None:
        if not self._can_generate():
            return

        self._generate_button.configure(  # type: ignore
            state="disabled",
            text="Génération en cours...",
            text_color=DesignSystem.Color.GRAY,
            fg_color=DesignSystem.Color.LESS_WHITE,
            hover_color=DesignSystem.Color.LEAST_WHITE,
        )
        self._back_button.configure(state="disabled")  # type: ignore

        self._status_display.add_message(
            message="Début de la génération...", message_type="information"
        )

        def generate_thread() -> None:
            try:
                self._status_display.add_message(
                    message="Validation des fichiers d'entrée...",
                    message_type="information",
                )

                additional_params: dict[str, Any] = self._get_generation_parameters()

                result_path: Path = self._controller.generate_report(
                    report_name=self._report_spec.name,
                    source_files=self._selected_files,
                    output_directory_path=self._output_path,  # type: ignore
                    month=self._selected_month,  # type: ignore
                    year=self._selected_year,  # type: ignore
                    **additional_params,
                )

                self.after(
                    ms=0,
                    func=lambda: self._on_generation_success(output_file=result_path),
                )

            except ValueError as validation_error:
                error_msg = str(validation_error)
                self.after(
                    ms=0,
                    func=lambda msg=error_msg: self._on_validation_error(
                        error_message=msg
                    ),
                )
            except FileNotFoundError as file_error:
                error_msg = f"Fichier manquant : {file_error}"
                self.after(
                    ms=0,
                    func=lambda msg=error_msg: self._on_validation_error(
                        error_message=msg
                    ),
                )
            except Exception as error:
                error_msg = str(error)
                self.after(
                    ms=0,
                    func=lambda msg=error_msg: self._on_generation_error(
                        error_message=msg
                    ),
                )

        thread: threading.Thread = threading.Thread(target=generate_thread, daemon=True)
        thread.start()

    def _on_validation_error(self, error_message: str) -> None:
        self._status_display.add_message(
            message=f"Erreur de validation : {error_message}", message_type="erreur"
        )
        self._status_display.add_message(
            message="Veuillez vérifier que vos fichiers correspondent aux exigences du rapport",
            message_type="avertissement",
        )

        self._generate_button.configure(text="Générer le rapport")  # type: ignore
        self._update_generate_button_state()
        self._back_button.configure(state="normal")  # type: ignore

    def _on_generation_success(self, output_file: Path) -> None:
        self._last_generated_file = output_file
        self._status_display.add_message(
            message=f"Rapport généré avec succès : {output_file}",
            message_type="succès",
        )

        self._generate_button.configure(text="Générer le rapport")  # type: ignore
        self._update_generate_button_state()
        self._back_button.configure(state="normal")  # type: ignore
        self._show_success_window()

    def _on_generation_error(self, error_message: str) -> None:
        self._status_display.add_message(
            message=f"Échec de la génération : {error_message}", message_type="erreur"
        )

        self._generate_button.configure(text="Générer le rapport")  # type: ignore
        self._update_generate_button_state()
        self._back_button.configure(state="normal")  # type: ignore

    def _show_success_window(self) -> None:
        if not self._last_generated_file:
            return

        dialog: SuccessWindow = SuccessWindow(  # type: ignore
            parent=self,
            output_file_path=self._last_generated_file,
        )
