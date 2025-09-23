from __future__ import annotations

# Standard library imports
import threading
from pathlib import Path
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.core.domain.enums.space_time import Month
from app.core.domain.models.report_specification import ReportSpecification
from app.presentation.gui.components.date_selector import DateSelector
from app.presentation.gui.components.file_selector import FileSelector
from app.presentation.gui.components.output_selector import OutputSelector
from app.presentation.gui.components.status_display import StatusDisplay
from app.presentation.gui.components.email_dialog import EmailDialog
from app.presentation.gui.controllers.report_controller import ReportController
from app.presentation.gui.styling.design_system import DesignSystem


class BaseReportView(ctk.CTkFrame):
    """Base class for all report views with common functionality."""

    __slots__ = (
        "_report_spec",
        "_controller",
        "_on_back",
        "_date_selector",
        "_file_selector",
        "_output_selector",
        "_status_display",
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
        # Self configuration - match MenuView exactly
        self.configure(  # type: ignore
            fg_color=DesignSystem.Color.LEAST_WHITE,
            corner_radius=DesignSystem.Roundness.MD,
        )

        # Configure grid
        self.grid_columnconfigure(index=0, weight=1)
        self.grid_rowconfigure(index=1, weight=1)

        # Header with back button (stays fixed)
        self._setup_header()

        # Scrollable content frame - match MenuView styling
        self._scrollable_frame = ctk.CTkScrollableFrame(
            master=self,
            fg_color=DesignSystem.Color.TRANSPARENT,
        )
        self._scrollable_frame.grid(row=1, column=0, padx=DesignSystem.Spacing.XS, pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.LG), sticky="nsew")  # type: ignore
        self._scrollable_frame.grid_columnconfigure(index=0, weight=1)

        # Setup common components
        self._setup_common_components()

        # Setup report-specific components (override in subclasses)
        self._setup_report_specific_components()

        # Setup action buttons
        self._setup_action_buttons()

        # Initialize the date selector values after UI is fully set up
        self._selected_month = self._date_selector.get_selected_month()
        self._selected_year = self._date_selector.get_selected_year()
        self._update_generate_button_state()

    def _setup_header(self) -> None:
        """Setup the header section with back button and title."""
        # Header frame - match MenuView structure and spacing
        header_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self, fg_color=DesignSystem.Color.TRANSPARENT
        )
        header_frame.grid(row=0, column=0, padx=DesignSystem.Spacing.LG, pady=(DesignSystem.Spacing.LG, DesignSystem.Spacing.XS), sticky="ew")  # type: ignore
        header_frame.grid_columnconfigure(index=1, weight=1)

        # Back button - styled to match design system
        self._back_button = ctk.CTkButton(
            master=header_frame,
            text="<",
            text_color=DesignSystem.Color.WHITE,
            fg_color=DesignSystem.Color.GRAY,
            hover_color=DesignSystem.Color.DARKER_GRAY,
            corner_radius=DesignSystem.Roundness.XS,
            font=ctk.CTkFont(size=DesignSystem.FontSize.BUTTON, weight="bold"),
            command=self._on_back,
            width=DesignSystem.Width.XS,
            height=DesignSystem.Height.SM,
        )
        self._back_button.grid(row=0, column=0, padx=DesignSystem.Spacing.NONE, sticky="w")  # type: ignore

        # Report info frame
        info_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=header_frame, fg_color=DesignSystem.Color.TRANSPARENT
        )
        info_frame.grid(row=0, column=1, sticky="ew")  # type: ignore
        info_frame.grid_columnconfigure(index=0, weight=1)

        # Report title - match MenuView header styling
        title_label: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text=self._report_spec.display_name,
            font=ctk.CTkFont(size=DesignSystem.FontSize.H2, weight="bold"),
            text_color=DesignSystem.Color.BLACK,
        )
        title_label.grid(row=0, column=0, padx=DesignSystem.Spacing.MD, pady=DesignSystem.Spacing.XS, sticky="w")  # type: ignore

    def _setup_common_components(self) -> None:
        """Setup components common to all reports."""

        # Date selector - match MenuView card spacing
        self._date_selector = DateSelector(
            parent=self._scrollable_frame, on_date_changed=self._on_date_changed
        )
        self._date_selector.grid(row=self._next_row, column=0, padx=DesignSystem.Spacing.SM, pady=DesignSystem.Spacing.SM, sticky="ew")  # type: ignore
        self._next_row += 1

        # Required files section
        self._create_required_files_section()

        # File selector - match MenuView card spacing
        self._file_selector = FileSelector(
            parent=self._scrollable_frame, on_files_changed=self._on_files_changed
        )
        self._file_selector.grid(row=self._next_row, column=0, padx=DesignSystem.Spacing.SM, pady=DesignSystem.Spacing.SM, sticky="ew")  # type: ignore
        self._next_row += 1

        # Output selector - match MenuView card spacing
        self._output_selector = OutputSelector(
            parent=self._scrollable_frame, on_output_changed=self._on_output_changed
        )
        self._output_selector.grid(row=self._next_row, column=0, padx=DesignSystem.Spacing.SM, pady=DesignSystem.Spacing.SM, sticky="ew")  # type: ignore
        self._next_row += 1

    def _setup_report_specific_components(self) -> None:
        """Override this method in subclasses to add report-specific components."""
        pass

    def _setup_action_buttons(self) -> None:
        """Setup the status display and action buttons."""
        # Status display - match MenuView card spacing
        self._status_display = StatusDisplay(parent=self._scrollable_frame)
        self._status_display.grid(row=self._next_row, column=0, padx=DesignSystem.Spacing.SM, pady=DesignSystem.Spacing.SM, sticky="ew")  # type: ignore
        self._next_row += 1

        # Button frame for Generate button
        button_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self._scrollable_frame,
            fg_color=DesignSystem.Color.TRANSPARENT,
        )
        button_frame.grid(row=self._next_row, column=0, padx=DesignSystem.Spacing.SM, pady=DesignSystem.Spacing.SM, sticky="ew")  # type: ignore
        button_frame.grid_columnconfigure(index=0, weight=1)

        # Generate button - starts with disabled styling (same as clear button in FileSelector)
        self._generate_button = ctk.CTkButton(
            master=button_frame,
            text="Générer le rapport",
            text_color=DesignSystem.Color.GRAY,
            fg_color=DesignSystem.Color.LESS_WHITE,
            hover_color=DesignSystem.Color.LEAST_WHITE,
            corner_radius=DesignSystem.Roundness.SM,
            font=ctk.CTkFont(size=DesignSystem.FontSize.BUTTON, weight="bold"),
            command=self._generate_report,
            height=40,
        )
        self._generate_button.grid(row=0, column=0, sticky="ew")  # type: ignore
        self._generate_button.configure(state="disabled")  # type: ignore

    def _create_required_files_section(self) -> None:
        # Required files frame - match MenuView card spacing
        req_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self._scrollable_frame,
            fg_color=DesignSystem.Color.TRANSPARENT,
        )
        req_frame.grid(row=self._next_row, column=0, padx=DesignSystem.Spacing.SM, pady=DesignSystem.Spacing.SM, sticky="ew")  # type: ignore
        req_frame.grid_columnconfigure(index=0, weight=1)
        self._next_row += 1

        # Title - match MenuView styling
        req_title: ctk.CTkLabel = ctk.CTkLabel(
            master=req_frame,
            text="Fichiers requis",
            font=ctk.CTkFont(size=DesignSystem.FontSize.BODY, weight="bold"),
            text_color=DesignSystem.Color.BLACK,
        )
        req_title.grid(row=0, column=0, pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM), sticky="w")  # type: ignore

        # Info box - explicitly style to override theme
        info_box: ctk.CTkFrame = ctk.CTkFrame(
            master=req_frame,
            fg_color=DesignSystem.Color.WHITE,
            corner_radius=DesignSystem.Roundness.SM,
        )
        info_box.grid(row=1, column=0, sticky="ew")  # type: ignore

        # Required files list
        req_text: str = self._get_required_files_text()

        req_label: ctk.CTkLabel = ctk.CTkLabel(
            master=info_box,
            text=req_text,
            font=ctk.CTkFont(size=DesignSystem.FontSize.BODY),
            text_color=DesignSystem.Color.BLACK,
            justify="left",
            anchor="w",
        )
        req_label.grid(row=0, column=0, padx=DesignSystem.Spacing.MD, pady=DesignSystem.Spacing.MD, sticky="w")  # type: ignore

    def _get_required_files_text(self) -> str:
        return (
            "Veuillez sélectionner les fichiers Excel requis pour ce rapport.\n"
            "Le système validera les fichiers sélectionnés avant la génération."
        )

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
        """Override in subclasses to add additional validation."""
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
            # Enable button with primary styling (yellow)
            self._generate_button.configure(  # type: ignore
                state="normal",
                text_color=DesignSystem.Color.WHITE,
                fg_color=DesignSystem.Color.PRIMARY,
                hover_color=DesignSystem.Color.DARKER_PRIMARY,
            )
        else:
            # Disable button with muted styling (same as clear button)
            self._generate_button.configure(  # type: ignore
                state="disabled",
                text_color=DesignSystem.Color.GRAY,
                fg_color=DesignSystem.Color.LESS_WHITE,
                hover_color=DesignSystem.Color.LEAST_WHITE,
            )

    def _get_generation_parameters(self) -> dict[str, Any]:
        """Override in subclasses to provide additional parameters."""
        return {}

    def _generate_report(self) -> None:
        if not self._can_generate():
            return

        # Disable buttons during processing - keep the disabled styling
        self._generate_button.configure(  # type: ignore
            state="disabled",
            text="Génération en cours...",
            text_color=DesignSystem.Color.GRAY,
            fg_color=DesignSystem.Color.LESS_WHITE,
            hover_color=DesignSystem.Color.LEAST_WHITE,
        )
        self._back_button.configure(state="disabled")  # type: ignore

        # Clear previous status messages
        self._status_display.clear_messages()
        self._status_display.add_message(
            message="Début de la génération...", message_type="information"
        )

        # Run generation in background thread
        def generate_thread() -> None:
            try:
                self._status_display.add_message(
                    message="Validation des fichiers d'entrée...",
                    message_type="information",
                )

                # Get additional parameters from subclass
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
                self.after(
                    ms=0,
                    func=lambda: self._on_validation_error(
                        error_message=str(validation_error)
                    ),
                )
            except FileNotFoundError as file_error:
                self.after(
                    ms=0,
                    func=lambda: self._on_validation_error(
                        error_message=f"Fichier manquant : {file_error}"
                    ),
                )
            except Exception as error:
                self.after(
                    ms=0,
                    func=lambda: self._on_generation_error(error_message=str(error)),
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
        # Reset to original text and update styling based on current state
        self._generate_button.configure(text="Générer le rapport")  # type: ignore
        self._update_generate_button_state()
        self._back_button.configure(state="normal")  # type: ignore

    def _on_generation_success(self, output_file: Path) -> None:
        self._last_generated_file = output_file
        self._status_display.add_message(
            message=f"Rapport généré avec succès : {output_file}",
            message_type="succès",
        )
        # Reset to original text and update styling based on current state
        self._generate_button.configure(text="Générer le rapport")  # type: ignore
        self._update_generate_button_state()
        self._back_button.configure(state="normal")  # type: ignore
        self._show_email_dialog()

    def _on_generation_error(self, error_message: str) -> None:
        self._status_display.add_message(
            message=f"Échec de la génération : {error_message}", message_type="erreur"
        )
        # Reset to original text and update styling based on current state
        self._generate_button.configure(text="Générer le rapport")  # type: ignore
        self._update_generate_button_state()
        self._back_button.configure(state="normal")  # type: ignore

    def _show_email_dialog(self) -> None:
        if not self._last_generated_file:
            return

        dialog: EmailDialog = EmailDialog(  # type: ignore
            parent=self,
            file_path=str(self._last_generated_file),
            on_send=self._send_email,
        )

    def _send_email(self, recipients: list[str], file_path: str) -> None:
        self._status_display.add_message(
            message=f"L'email sera envoyé à : {', '.join(recipients)}",
            message_type="succès",
        )
        print(f"Envoi de {file_path} à : {recipients}")
