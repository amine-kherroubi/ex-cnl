from __future__ import annotations

# Standard library imports
import threading
from pathlib import Path

# Third-party imports
import customtkinter as ctk

# Local application imports
from gui.components.file_selector import FileSelector
from gui.components.report_selector import ReportSelector
from gui.components.output_selector import OutputSelector
from gui.components.status_display import StatusDisplay
from gui.models.gui_state import GUIState
from gui.controllers.document_controller import DocumentController


class MainWindow(ctk.CTk):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()

        # Window configuration
        self.title("Document Generator")
        self.geometry("800x600")
        self.minsize(600, 500)

        # Set theme
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # Initialize state and controller
        self._state = GUIState()
        self._controller = DocumentController()

        # Setup UI
        self._setup_ui()

        # Load available reports
        self._load_available_reports()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        # Configure grid weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            self, text="Document Generator", font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(3, weight=1)

        # File selector
        self._file_selector = FileSelector(
            main_frame, on_files_changed=self._on_files_changed
        )
        self._file_selector.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        # Report selector
        self._report_selector = ReportSelector(
            main_frame, on_report_changed=self._on_report_changed
        )
        self._report_selector.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Output selector
        self._output_selector = OutputSelector(
            main_frame, on_output_changed=self._on_output_changed
        )
        self._output_selector.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Status display
        self._status_display = StatusDisplay(main_frame)
        self._status_display.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nsew")

        # Generate button
        self._generate_button = ctk.CTkButton(
            main_frame,
            text="Generate Report",
            command=self._generate_report,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self._generate_button.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")
        self._generate_button.configure(state="disabled")

    def _load_available_reports(self) -> None:
        """Load available reports from the controller."""
        try:
            reports = self._controller.get_available_reports()
            self._report_selector.set_reports(reports)
            self._status_display.add_message("Application ready", "info")
        except Exception as e:
            self._status_display.add_message(
                f"Error loading reports: {str(e)}", "error"
            )

    def _on_files_changed(self, files: list[Path]) -> None:
        """Handle file selection changes."""
        self._state.selected_files = files
        self._update_generate_button_state()

        if files:
            self._status_display.add_message(f"Selected {len(files)} file(s)", "info")
        else:
            self._status_display.add_message("No files selected", "warning")

    def _on_report_changed(self, report_name: str | None) -> None:
        """Handle report selection changes."""
        self._state.selected_report = report_name
        self._update_generate_button_state()

        if report_name:
            self._status_display.add_message(f"Selected report: {report_name}", "info")
        else:
            self._status_display.add_message("No report selected", "warning")

    def _on_output_changed(self, output_path: Path | None) -> None:
        """Handle output path selection changes."""
        self._state.output_path = output_path
        self._update_generate_button_state()

        if output_path:
            self._status_display.add_message(f"Output folder: {output_path}", "info")
        else:
            self._status_display.add_message("No output folder selected", "warning")

    def _update_generate_button_state(self) -> None:
        """Update the generate button state based on current selections."""
        can_generate = (
            self._state.selected_report is not None
            and len(self._state.selected_files) > 0
            and self._state.output_path is not None
        )

        if can_generate:
            self._generate_button.configure(state="normal")
        else:
            self._generate_button.configure(state="disabled")

    def _generate_report(self) -> None:
        """Generate the selected report."""
        if not all(
            [
                self._state.selected_report,
                self._state.selected_files,
                self._state.output_path,
            ]
        ):
            return

        # Disable generate button during processing
        self._generate_button.configure(state="disabled", text="Generating...")

        # Clear previous status messages
        self._status_display.clear_messages()
        self._status_display.add_message("Starting report generation...", "info")

        # Run generation in background thread
        def generate_thread() -> None:
            try:
                result = self._controller.generate_document(
                    report_name=self._state.selected_report,  # type: ignore
                    input_files=self._state.selected_files,
                    output_path=self._state.output_path,  # type: ignore
                )

                # Update UI on success (thread-safe)
                self.after(0, lambda: self._on_generation_success(result))

            except Exception as e:
                # Update UI on error (thread-safe)
                self.after(0, lambda: self._on_generation_error(str(e)))

        thread = threading.Thread(target=generate_thread, daemon=True)
        thread.start()

    def _on_generation_success(self, output_file: str) -> None:
        """Handle successful report generation."""
        self._status_display.add_message(
            f"Report generated successfully: {output_file}", "success"
        )
        self._generate_button.configure(state="normal", text="Generate Report")

    def _on_generation_error(self, error_message: str) -> None:
        """Handle report generation error."""
        self._status_display.add_message(f"Generation failed: {error_message}", "error")
        self._generate_button.configure(state="normal", text="Generate Report")


def main() -> None:
    """Main entry point."""
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
