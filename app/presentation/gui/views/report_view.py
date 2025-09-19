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
from app.presentation.gui.styling.design_system import Color, Spacing, FontSize


class ReportView(ctk.CTkFrame):
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

        self._setup_ui()

    def _setup_ui(self) -> None:
        # Configure grid
        self.grid_columnconfigure(index=0, weight=1)
        self.grid_rowconfigure(index=1, weight=1)

        # Header with back button (stays fixed)
        header_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self, fg_color=Color.TRANSPARENT
        )
        header_frame.grid(row=0, column=0, padx=Spacing.LG, pady=(Spacing.LG, Spacing.SM), sticky="ew")  # type: ignore
        header_frame.grid_columnconfigure(index=1, weight=1)

        # Back button - secondary style
        self._back_button: ctk.CTkButton = ctk.CTkButton(
            master=header_frame,
            text="Retour",
            command=self._on_back,
            width=100,
            height=32,
            font=ctk.CTkFont(size=FontSize.LABEL),
        )
        self._back_button.grid(row=0, column=0, padx=(Spacing.NONE, Spacing.LG), sticky="w")  # type: ignore

        # Report info
        info_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=header_frame, fg_color=Color.TRANSPARENT
        )
        info_frame.grid(row=0, column=1, sticky="ew")  # type: ignore

        # Report title
        title_label: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text=self._report_spec.display_name,
            font=ctk.CTkFont(size=FontSize.H3, weight="bold"),
        )
        title_label.grid(row=0, column=0, sticky="w")  # type: ignore

        # Scrollable content frame
        scrollable_frame: ctk.CTkScrollableFrame = ctk.CTkScrollableFrame(master=self)
        scrollable_frame.grid(row=1, column=0, padx=Spacing.LG, pady=(Spacing.SM, Spacing.LG), sticky="nsew")  # type: ignore
        scrollable_frame.grid_columnconfigure(index=0, weight=1)

        # Required files section
        self._create_required_files_section(parent=scrollable_frame)

        # Date selector
        self._date_selector: DateSelector = DateSelector(
            parent=scrollable_frame, on_date_changed=self._on_date_changed
        )
        self._date_selector.grid(row=1, column=0, padx=Spacing.LG, pady=(Spacing.LG, Spacing.SM), sticky="ew")  # type: ignore

        # File selector
        self._file_selector: FileSelector = FileSelector(
            parent=scrollable_frame, on_files_changed=self._on_files_changed
        )
        self._file_selector.grid(row=2, column=0, padx=Spacing.LG, pady=(Spacing.SM, Spacing.SM), sticky="ew")  # type: ignore

        # Output selector
        self._output_selector: OutputSelector = OutputSelector(
            parent=scrollable_frame, on_output_changed=self._on_output_changed
        )
        self._output_selector.grid(row=3, column=0, padx=Spacing.LG, pady=(Spacing.SM, Spacing.SM), sticky="ew")  # type: ignore

        # Status display
        self._status_display: StatusDisplay = StatusDisplay(parent=scrollable_frame)
        self._status_display.grid(row=4, column=0, padx=Spacing.LG, pady=(Spacing.SM, Spacing.LG), sticky="ew")  # type: ignore

        # Button frame for Generate and Email buttons
        button_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=scrollable_frame, fg_color=Color.TRANSPARENT
        )
        button_frame.grid(row=5, column=0, padx=Spacing.LG, pady=(Spacing.NONE, Spacing.LG), sticky="ew")  # type: ignore
        button_frame.grid_columnconfigure(index=0, weight=1)

        # Generate button
        self._generate_button: ctk.CTkButton = ctk.CTkButton(
            master=button_frame,
            text="Générer le rapport",
            command=self._generate_report,
            height=40,
            font=ctk.CTkFont(size=FontSize.LABEL, weight="bold"),
        )
        self._generate_button.grid(row=0, column=0, sticky="ew")  # type: ignore
        self._generate_button.configure(state="disabled")  # type: ignore

        # Initialize the date selector values after UI is fully set up
        self._selected_month = self._date_selector.get_selected_month()
        self._selected_year = self._date_selector.get_selected_year()
        self._update_generate_button_state()

    def _create_required_files_section(self, parent: Any) -> None:
        # Required files frame
        req_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=parent, fg_color=Color.TRANSPARENT
        )
        req_frame.grid(row=0, column=0, padx=Spacing.LG, pady=(Spacing.LG, Spacing.NONE), sticky="ew")  # type: ignore
        req_frame.grid_columnconfigure(index=0, weight=1)

        # Title
        req_title: ctk.CTkLabel = ctk.CTkLabel(
            master=req_frame,
            text="Fichiers requis",
            font=ctk.CTkFont(size=FontSize.LABEL, weight="bold"),
        )
        req_title.grid(row=0, column=0, pady=(Spacing.NONE, Spacing.SM), sticky="w")  # type: ignore

        # Info box - uses theme defaults
        info_box: ctk.CTkFrame = ctk.CTkFrame(master=req_frame)
        info_box.grid(row=1, column=0, sticky="ew")  # type: ignore

        # Required files list
        req_text: str = self._get_required_files_text()

        req_label: ctk.CTkLabel = ctk.CTkLabel(
            master=info_box,
            text=req_text,
            font=ctk.CTkFont(size=FontSize.BODY),
            justify="left",
            anchor="w",
        )
        req_label.grid(row=0, column=0, padx=Spacing.MD, pady=Spacing.MD, sticky="w")  # type: ignore

    def _get_required_files_text(self) -> str:
        return (
            "Veuillez sélectionner les fichiers Excel requis pour ce rapport.\n"
            "Le système validera les fichiers sélectionnés avant la génération."
        )

    def _on_date_changed(self, month: Month | None, year: int | None) -> None:
        self._selected_month = month
        self._selected_year = year

        # Only update button state if it exists (to handle initialization order)
        if hasattr(self, "_generate_button"):
            self._update_generate_button_state()

        if month and year and hasattr(self, "_status_display"):
            self._status_display.add_message(
                message=f"Période sélectionnée : {month.value.capitalize()} {year}",
                message_type="information",
            )

    def _on_files_changed(self, files: list[Path]) -> None:
        self._selected_files = files

        # Only update button state if it exists (to handle initialization order)
        if hasattr(self, "_generate_button"):
            self._update_generate_button_state()

        if hasattr(self, "_status_display"):
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

        # Only update button state if it exists (to handle initialization order)
        if hasattr(self, "_generate_button"):
            self._update_generate_button_state()

        if hasattr(self, "_status_display"):
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

    def _update_generate_button_state(self) -> None:
        # Ensure button exists before updating
        if not hasattr(self, "_generate_button"):
            return

        can_generate: bool = (
            len(self._selected_files) > 0
            and self._output_path is not None
            and self._selected_month is not None
            and self._selected_year is not None
        )

        if can_generate:
            self._generate_button.configure(state="normal")  # type: ignore
        else:
            self._generate_button.configure(state="disabled")  # type: ignore

    def _generate_report(self) -> None:
        if not all(
            [
                self._selected_files,
                self._output_path,
                self._selected_month,
                self._selected_year,
            ]
        ):
            return

        # Disable buttons during processing
        self._generate_button.configure(state="disabled", text="Génération en cours...")  # type: ignore
        self._back_button.configure(state="disabled")  # type: ignore

        # Clear previous status messages
        self._status_display.clear_messages()
        self._status_display.add_message(
            message="Début de la génération...", message_type="information"
        )

        # Run generation in background thread
        def generate_thread() -> None:
            try:
                # First validate the files
                self._status_display.add_message(
                    message="Validation des fichiers d'entrée...",
                    message_type="information",
                )

                # Use the report's name (key) instead of display_name
                report_name = self._report_spec.name

                result_path: Path = self._controller.generate_report(
                    report_name=report_name,  # Use internal name, not display_name
                    source_files=self._selected_files,
                    output_directory_path=self._output_path,  # type: ignore
                    month=self._selected_month,  # type: ignore
                    year=self._selected_year,  # type: ignore
                )

                # Update UI on success (thread-safe)
                self.after(
                    ms=0,
                    func=lambda: self._on_generation_success(output_file=result_path),
                )

            except ValueError as validation_error:
                # Handle validation errors specifically
                self.after(
                    ms=0,
                    func=lambda: self._on_validation_error(
                        error_message=str(validation_error)
                    ),
                )
            except FileNotFoundError as file_error:
                # Handle missing file errors
                self.after(
                    ms=0,
                    func=lambda: self._on_validation_error(
                        error_message=f"Fichier manquant : {file_error}"
                    ),
                )
            except Exception as error:
                # Handle other errors
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
        self._generate_button.configure(state="normal", text="Générer le rapport")  # type: ignore
        self._back_button.configure(state="normal")  # type: ignore

    def _on_generation_success(self, output_file: Path) -> None:
        self._last_generated_file = output_file
        self._status_display.add_message(
            message=f"Rapport généré avec succès : {output_file}",
            message_type="succès",
        )
        self._generate_button.configure(state="normal", text="Générer le rapport")  # type: ignore
        self._back_button.configure(state="normal")  # type: ignore

        # Show email dialog
        self._show_email_dialog()

    def _on_generation_error(self, error_message: str) -> None:
        self._status_display.add_message(
            message=f"Échec de la génération : {error_message}", message_type="erreur"
        )
        self._generate_button.configure(state="normal", text="Générer le rapport")  # type: ignore
        self._back_button.configure(state="normal")  # type: ignore

    def _show_email_dialog(self) -> None:
        if not self._last_generated_file:
            return

        dialog: EmailDialog = EmailDialog(  # type: ignore
            parent=self,
            file_path=str(self._last_generated_file),  # Convert Path to str for dialog
            on_send=self._send_email,
        )

    def _send_email(self, recipients: list[str], file_path: str) -> None:
        # This is where you would implement actual email sending
        # For now, just show a success message
        self._status_display.add_message(
            message=f"L'email sera envoyé à : {', '.join(recipients)}",
            message_type="succès",
        )
        print(f"Envoi de {file_path} à : {recipients}")
