from __future__ import annotations

# Standard library imports
import threading
from pathlib import Path
from typing import Any

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from gui.components.file_selector import FileSelector
from gui.components.report_selector import ReportSelector
from gui.components.output_selector import OutputSelector
from gui.components.status_display import StatusDisplay
from gui.models.gui_state import GUIState
from gui.controllers.document_controller import DocumentController


class MainWindow(ctk.CTk):
    __slots__ = (
        "_state",
        "_controller",
        "_file_selector",
        "_report_selector",
        "_output_selector",
        "_status_display",
        "_generate_button",
    )

    def __init__(self) -> None:
        super().__init__()  # type: ignore

        # Window configuration
        self.title(string="Document Generator")
        self.geometry(geometry_string="800x600")
        self.minsize(width=600, height=500)

        # Set theme
        ctk.set_appearance_mode(mode_string="system")
        ctk.set_default_color_theme(color_string="green")

        # Initialize state and controller
        self._state: GUIState = GUIState()
        self._controller: DocumentController = DocumentController()

        # Setup UI
        self._setup_ui()

        # Load available reports
        self._load_available_reports()

    def _setup_ui(self) -> None:
        # Configure grid weights
        self.grid_columnconfigure(index=0, weight=1)
        self.grid_rowconfigure(index=1, weight=1)

        # Title
        title_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self,
            text="Document Generator",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")  # type: ignore

        # Main container
        main_frame: ctk.CTkFrame = ctk.CTkFrame(master=self)
        main_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")  # type: ignore
        main_frame.grid_columnconfigure(index=0, weight=1)
        main_frame.grid_rowconfigure(index=3, weight=1)

        # File selector
        self._file_selector: FileSelector = FileSelector(
            parent=main_frame, on_files_changed=self._on_files_changed
        )
        self._file_selector.grid(row=0, column=0, padx=20, pady=20, sticky="ew")  # type: ignore

        # Report selector
        self._report_selector: ReportSelector = ReportSelector(
            parent=main_frame, on_report_changed=self._on_report_changed
        )
        self._report_selector.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")  # type: ignore

        # Output selector
        self._output_selector: OutputSelector = OutputSelector(
            parent=main_frame, on_output_changed=self._on_output_changed
        )
        self._output_selector.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")  # type: ignore

        # Status display
        self._status_display: StatusDisplay = StatusDisplay(parent=main_frame)
        self._status_display.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nsew")  # type: ignore

        # Generate button
        self._generate_button: ctk.CTkButton = ctk.CTkButton(
            master=main_frame,
            text="Generate Report",
            command=self._generate_report,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self._generate_button.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")  # type: ignore
        self._generate_button.configure(state="disabled")  # type: ignore

    def _load_available_reports(self) -> None:
        try:
            reports: dict[str, Any] = self._controller.get_available_reports()
            self._report_selector.set_reports(reports=reports)
            self._status_display.add_message(
                message="Application ready", message_type="info"
            )
        except Exception as e:
            self._status_display.add_message(
                message=f"Error loading reports: {str(e)}", message_type="error"
            )

    def _on_files_changed(self, files: list[Path]) -> None:
        self._state.selected_files = files
        self._update_generate_button_state()

        if files:
            self._status_display.add_message(
                message=f"Selected {len(files)} file(s)", message_type="info"
            )
        else:
            self._status_display.add_message(
                message="No files selected", message_type="warning"
            )

    def _on_report_changed(self, report_name: str | None) -> None:
        self._state.selected_report = report_name
        self._update_generate_button_state()

        if report_name:
            self._status_display.add_message(
                message=f"Selected report: {report_name}", message_type="info"
            )
        else:
            self._status_display.add_message(
                message="No report selected", message_type="warning"
            )

    def _on_output_changed(self, output_path: Path | None) -> None:
        self._state.output_path = output_path
        self._update_generate_button_state()

        if output_path:
            self._status_display.add_message(
                message=f"Output folder: {output_path}", message_type="info"
            )
        else:
            self._status_display.add_message(
                message="No output folder selected", message_type="warning"
            )

    def _update_generate_button_state(self) -> None:
        can_generate: bool = (
            self._state.selected_report is not None
            and len(self._state.selected_files) > 0
            and self._state.output_path is not None
        )

        if can_generate:
            self._generate_button.configure(state="normal")  # type: ignore
        else:
            self._generate_button.configure(state="disabled")  # type: ignore

    def _generate_report(self) -> None:
        if not all(
            [
                self._state.selected_report,
                self._state.selected_files,
                self._state.output_path,
            ]
        ):
            return

        # Disable generate button during processing
        self._generate_button.configure(state="disabled", text="Generating...")  # type: ignore

        # Clear previous status messages
        self._status_display.clear_messages()
        self._status_display.add_message(
            message="Starting report generation...", message_type="info"
        )

        # Run generation in background thread
        def generate_thread() -> None:
            try:
                result: str = self._controller.generate_document(
                    report_name=self._state.selected_report,  # type: ignore
                    input_files=self._state.selected_files,
                    output_path=self._state.output_path,  # type: ignore
                )

                # Update UI on success (thread-safe)
                self.after(
                    ms=0, func=lambda: self._on_generation_success(output_file=result)
                )

            except Exception as e:
                # Update UI on error (thread-safe)
                self.after(
                    ms=0, func=lambda: self._on_generation_error(error_message=str(e))
                )

        thread: threading.Thread = threading.Thread(target=generate_thread, daemon=True)
        thread.start()

    def _on_generation_success(self, output_file: str) -> None:
        self._status_display.add_message(
            message=f"Report generated successfully: {output_file}",
            message_type="success",
        )
        self._generate_button.configure(state="normal", text="Generate Report")  # type: ignore

    def _on_generation_error(self, error_message: str) -> None:
        self._status_display.add_message(
            message=f"Generation failed: {error_message}", message_type="error"
        )
        self._generate_button.configure(state="normal", text="Generate Report")  # type: ignore


def main() -> None:
    app: MainWindow = MainWindow()
    app.mainloop()  # type: ignore


if __name__ == "__main__":
    main()
