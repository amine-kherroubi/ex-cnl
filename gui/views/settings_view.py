from __future__ import annotations

# Standard library imports
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore


class SettingsView(ctk.CTkFrame):
    __slots__ = (
        "_document_name",
        "_on_back",
        "_back_button",
        "_save_button",
        "_settings_widgets",
    )

    def __init__(
        self,
        parent: Any,
        document_name: str,
        on_back: Callable[[], None],
    ) -> None:
        super().__init__(master=parent)  # type: ignore

        self._document_name: str = document_name
        self._on_back: Callable[[], None] = on_back
        self._settings_widgets: dict[str, Any] = {}

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

        # Settings title
        title_label: ctk.CTkLabel = ctk.CTkLabel(
            master=header_frame,
            text=f"Settings for {self._document_name}",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        title_label.grid(row=0, column=1, sticky="w")  # type: ignore

        # Main content scrollable frame
        content_frame: ctk.CTkScrollableFrame = ctk.CTkScrollableFrame(master=self)
        content_frame.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="nsew")  # type: ignore
        content_frame.grid_columnconfigure(index=0, weight=1)

        # Create settings based on document type
        if (
            "mensuelle" in self._document_name.lower()
            or "monthly" in self._document_name.lower()
        ):
            self._create_monthly_settings(parent=content_frame)
        else:
            self._create_generic_settings(parent=content_frame)

        # Bottom buttons frame
        buttons_frame: ctk.CTkFrame = ctk.CTkFrame(master=self, fg_color="transparent")
        buttons_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")  # type: ignore
        buttons_frame.grid_columnconfigure(index=0, weight=1)

        # Save button
        self._save_button: ctk.CTkButton = ctk.CTkButton(
            master=buttons_frame,
            text="Save Settings",
            command=self._save_settings,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self._save_button.grid(row=0, column=1, padx=(10, 0), sticky="e")  # type: ignore

        # Cancel button
        cancel_button: ctk.CTkButton = ctk.CTkButton(
            master=buttons_frame,
            text="Cancel",
            command=self._on_back,
            height=40,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray80", "gray30"),
            border_width=2,
            font=ctk.CTkFont(size=14),
        )
        cancel_button.grid(row=0, column=0, sticky="w")  # type: ignore

    def _create_monthly_settings(self, parent: Any) -> None:
        # Programs section
        programs_section: SettingsSection = SettingsSection(
            parent=parent,
            title="Programs Configuration",
            description="Select which programs to include in the monthly activity report",
        )
        programs_section.grid(row=0, column=0, padx=10, pady=10, sticky="ew")  # type: ignore

        # Create program checkboxes
        programs: list[str] = [
            "Program Alpha",
            "Program Beta",
            "Program Gamma",
            "Program Delta",
            "Program Epsilon",
        ]

        for idx, program in enumerate(programs):
            checkbox: ctk.CTkCheckBox = ctk.CTkCheckBox(
                master=programs_section.get_content_frame(),
                text=program,
                font=ctk.CTkFont(size=13),
            )
            checkbox.grid(row=idx, column=0, padx=20, pady=5, sticky="w")  # type: ignore
            self._settings_widgets[f"program_{idx}"] = checkbox

        # Date range section
        date_section: SettingsSection = SettingsSection(
            parent=parent,
            title="Date Range Settings",
            description="Configure the default date range for report generation",
        )
        date_section.grid(row=1, column=0, padx=10, pady=10, sticky="ew")  # type: ignore

        date_frame: ctk.CTkFrame = date_section.get_content_frame()

        # Date range option
        date_label: ctk.CTkLabel = ctk.CTkLabel(
            master=date_frame,
            text="Default Period:",
            font=ctk.CTkFont(size=13),
        )
        date_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")  # type: ignore

        date_option: ctk.CTkOptionMenu = ctk.CTkOptionMenu(
            master=date_frame,
            values=["Current Month", "Previous Month", "Last 30 Days", "Custom"],
            font=ctk.CTkFont(size=13),
        )
        date_option.grid(row=0, column=1, padx=10, pady=10, sticky="w")  # type: ignore
        self._settings_widgets["date_range"] = date_option

    def _create_generic_settings(self, parent: Any) -> None:
        # General settings section
        general_section: SettingsSection = SettingsSection(
            parent=parent,
            title="General Settings",
            description="Configure general options for this document type",
        )
        general_section.grid(row=0, column=0, padx=10, pady=10, sticky="ew")  # type: ignore

        general_frame: ctk.CTkFrame = general_section.get_content_frame()

        # Output format
        format_label: ctk.CTkLabel = ctk.CTkLabel(
            master=general_frame,
            text="Output Format:",
            font=ctk.CTkFont(size=13),
        )
        format_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")  # type: ignore

        format_option: ctk.CTkOptionMenu = ctk.CTkOptionMenu(
            master=general_frame,
            values=["Excel (.xlsx)", "CSV (.csv)", "PDF (.pdf)"],
            font=ctk.CTkFont(size=13),
        )
        format_option.grid(row=0, column=1, padx=10, pady=10, sticky="w")  # type: ignore
        self._settings_widgets["output_format"] = format_option

        # Processing options section
        processing_section: SettingsSection = SettingsSection(
            parent=parent,
            title="Processing Options",
            description="Configure how the data should be processed",
        )
        processing_section.grid(row=1, column=0, padx=10, pady=10, sticky="ew")  # type: ignore

        processing_frame: ctk.CTkFrame = processing_section.get_content_frame()

        # Validation checkbox
        validation_checkbox: ctk.CTkCheckBox = ctk.CTkCheckBox(
            master=processing_frame,
            text="Perform data validation before processing",
            font=ctk.CTkFont(size=13),
        )
        validation_checkbox.grid(row=0, column=0, padx=20, pady=5, sticky="w")  # type: ignore
        validation_checkbox.select()  # type: ignore
        self._settings_widgets["validate_data"] = validation_checkbox

        # Duplicate handling
        duplicates_checkbox: ctk.CTkCheckBox = ctk.CTkCheckBox(
            master=processing_frame,
            text="Remove duplicate entries",
            font=ctk.CTkFont(size=13),
        )
        duplicates_checkbox.grid(row=1, column=0, padx=20, pady=5, sticky="w")  # type: ignore
        self._settings_widgets["remove_duplicates"] = duplicates_checkbox

    def _save_settings(self) -> None:
        # TODO: Implement actual settings saving logic
        # For now, just show a message and go back
        print(f"Saving settings for {self._document_name}")

        # Collect all settings values
        settings_values: dict[str, Any] = {}
        for key, widget in self._settings_widgets.items():
            if isinstance(widget, ctk.CTkCheckBox):
                settings_values[key] = widget.get()  # type: ignore
            elif isinstance(widget, ctk.CTkOptionMenu):
                settings_values[key] = widget.get()  # type: ignore

        print(f"Settings values: {settings_values}")

        # Return to menu
        self._on_back()


class SettingsSection(ctk.CTkFrame):
    __slots__ = ("_title", "_description", "_content_frame")

    def __init__(
        self,
        parent: Any,
        title: str,
        description: str,
    ) -> None:
        super().__init__(master=parent)  # type: ignore

        self._title: str = title
        self._description: str = description

        self._setup_ui()

    def _setup_ui(self) -> None:
        # Configure grid
        self.grid_columnconfigure(index=0, weight=1)

        # Section styling
        self.configure(fg_color=("gray90", "gray20"), corner_radius=10)  # type: ignore

        # Title
        title_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self,
            text=self._title,
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        title_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")  # type: ignore

        # Description
        desc_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self,
            text=self._description,
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60"),
        )
        desc_label.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")  # type: ignore

        # Content frame
        self._content_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self, fg_color="transparent"
        )
        self._content_frame.grid(row=2, column=0, padx=5, pady=(0, 15), sticky="ew")  # type: ignore
        self._content_frame.grid_columnconfigure(index=0, weight=1)

    def get_content_frame(self) -> ctk.CTkFrame:
        return self._content_frame
