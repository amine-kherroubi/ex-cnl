from __future__ import annotations

# Standard library imports
import threading
from pathlib import Path
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from gui.components.file_selector import FileSelector
from gui.components.output_selector import OutputSelector
from gui.components.status_display import StatusDisplay
from gui.controllers.document_controller import DocumentController


class DocumentView(ctk.CTkFrame):
    __slots__ = (
        "_document_name",
        "_document_spec",
        "_controller",
        "_on_back",
        "_file_selector",
        "_output_selector",
        "_status_display",
        "_generate_button",
        "_back_button",
        "_selected_files",
        "_output_path",
    )

    def __init__(
        self,
        parent: Any,
        document_name: str,
        document_spec: Any,
        controller: DocumentController,
        on_back: Callable[[], None],
    ) -> None:
        super().__init__(master=parent)  # type: ignore

        self._document_name: str = document_name
        self._document_spec: Any = document_spec
        self._controller: DocumentController = controller
        self._on_back: Callable[[], None] = on_back
        self._selected_files: list[Path] = []
        self._output_path: Path | None = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        # Configure grid
        self.grid_columnconfigure(index=0, weight=1)
        self.grid_rowconfigure(index=1, weight=1)

        # Header with back button
        header_frame: ctk.CTkFrame = ctk.CTkFrame(master=self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")  # type: ignore
        header_frame.grid_columnconfigure(index=1, weight=1)

        # Back button
        self._back_button: ctk.CTkButton = ctk.CTkButton(
            master=header_frame,
            text="← Back",
            command=self._on_back,
            width=100,
            height=32,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray80", "gray30"),
            font=ctk.CTkFont(size=14),
        )
        self._back_button.grid(row=0, column=0, padx=(0, 20), sticky="w")  # type: ignore

        # Document info
        info_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=header_frame, fg_color="transparent"
        )
        info_frame.grid(row=0, column=1, sticky="ew")  # type: ignore

        # Extract document info
        display_name: str = getattr(
            self._document_spec, "display_name", self._document_name
        )
        description: str = getattr(
            self._document_spec, "description", "No description available"
        )

        # Document title
        title_label: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text=display_name,
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        title_label.grid(row=0, column=0, sticky="w")  # type: ignore

        # Document description
        desc_label: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text=description,
            font=ctk.CTkFont(size=13),
            text_color=("gray30", "gray70"),
        )
        desc_label.grid(row=1, column=0, pady=(5, 0), sticky="w")  # type: ignore

        # Main content frame
        content_frame: ctk.CTkFrame = ctk.CTkFrame(master=self)
        content_frame.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="nsew")  # type: ignore
        content_frame.grid_columnconfigure(index=0, weight=1)
        content_frame.grid_rowconfigure(index=2, weight=1)

        # Required files section
        self._create_required_files_section(parent=content_frame)

        # File selector
        self._file_selector: FileSelector = FileSelector(
            parent=content_frame, on_files_changed=self._on_files_changed
        )
        self._file_selector.grid(row=1, column=0, padx=20, pady=(20, 10), sticky="ew")  # type: ignore

        # Output selector
        self._output_selector: OutputSelector = OutputSelector(
            parent=content_frame, on_output_changed=self._on_output_changed
        )
        self._output_selector.grid(row=2, column=0, padx=20, pady=(10, 10), sticky="ew")  # type: ignore

        # Status display
        self._status_display: StatusDisplay = StatusDisplay(parent=content_frame)
        self._status_display.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="nsew")  # type: ignore

        # Generate button
        self._generate_button: ctk.CTkButton = ctk.CTkButton(
            master=content_frame,
            text="Generate Document",
            command=self._generate_document,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self._generate_button.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")  # type: ignore
        self._generate_button.configure(state="disabled")  # type: ignore

    def _create_required_files_section(self, parent: Any) -> None:
        # Required files frame
        req_frame: ctk.CTkFrame = ctk.CTkFrame(master=parent, fg_color="transparent")
        req_frame.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="ew")  # type: ignore
        req_frame.grid_columnconfigure(index=0, weight=1)

        # Title
        req_title: ctk.CTkLabel = ctk.CTkLabel(
            master=req_frame,
            text="Required Files",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        req_title.grid(row=0, column=0, pady=(0, 10), sticky="w")  # type: ignore

        # Info box
        info_box: ctk.CTkFrame = ctk.CTkFrame(
            master=req_frame,
            fg_color=("gray85", "gray25"),
            corner_radius=8,
        )
        info_box.grid(row=1, column=0, sticky="ew")  # type: ignore

        # Required files list (placeholder - would be populated from document spec)
        req_text: str = self._get_required_files_text()

        req_label: ctk.CTkLabel = ctk.CTkLabel(
            master=info_box,
            text=req_text,
            font=ctk.CTkFont(size=13),
            justify="left",
            anchor="w",
        )
        req_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")  # type: ignore

    def _get_required_files_text(self) -> str:
        # This would be extracted from document spec in real implementation
        # For now, return a generic message
        return (
            "📁 Please select the required Excel files for this document type.\n"
            "📋 The system will validate the selected files before generation."
        )

    def _on_files_changed(self, files: list[Path]) -> None:
        self._selected_files = files
        self._update_generate_button_state()

        if files:
            self._status_display.add_message(
                message=f"Selected {len(files)} file(s)", message_type="info"
            )
        else:
            self._status_display.add_message(
                message="No files selected", message_type="warning"
            )

    def _on_output_changed(self, output_path: Path | None) -> None:
        self._output_path = output_path
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
            len(self._selected_files) > 0 and self._output_path is not None
        )

        if can_generate:
            self._generate_button.configure(state="normal")  # type: ignore
        else:
            self._generate_button.configure(state="disabled")  # type: ignore

    def _generate_document(self) -> None:
        if not all([self._selected_files, self._output_path]):
            return

        # Disable buttons during processing
        self._generate_button.configure(state="disabled", text="Generating...")  # type: ignore
        self._back_button.configure(state="disabled")  # type: ignore

        # Clear previous status messages
        self._status_display.clear_messages()
        self._status_display.add_message(
            message="Starting document generation...", message_type="info"
        )

        # Run generation in background thread
        def generate_thread() -> None:
            try:
                result: str = self._controller.generate_document(
                    report_name=self._document_name,
                    input_files=self._selected_files,
                    output_path=self._output_path,  # type: ignore
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
            message=f"Document generated successfully: {output_file}",
            message_type="success",
        )
        self._generate_button.configure(state="normal", text="Generate Document")  # type: ignore
        self._back_button.configure(state="normal")  # type: ignore

    def _on_generation_error(self, error_message: str) -> None:
        self._status_display.add_message(
            message=f"Generation failed: {error_message}", message_type="error"
        )
        self._generate_button.configure(state="normal", text="Generate Document")  # type: ignore
        self._back_button.configure(state="normal")  # type: ignore
