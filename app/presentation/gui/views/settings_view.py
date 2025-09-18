from __future__ import annotations

# Standard library imports
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.presentation.gui.styling.design_system import Color, Spacing, FontSize


class SettingsView(ctk.CTkFrame):
    __slots__ = (
        "_report_name",
        "_on_back",
        "_back_button",
        "_save_button",
        "_settings_widgets",
    )

    def __init__(
        self,
        parent: Any,
        report_name: str,
        on_back: Callable[[], None],
    ) -> None:
        super().__init__(master=parent)  # type: ignore

        self._report_name: str = report_name
        self._on_back: Callable[[], None] = on_back
        self._settings_widgets: dict[str, Any] = {}

        self._setup_ui()

    def _setup_ui(self) -> None:
        # Configure grid
        self.grid_columnconfigure(index=0, weight=1)
        self.grid_rowconfigure(index=1, weight=1)

        # Header with back button
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
            height=35,
            fg_color=Color.TRANSPARENT,
            border_width=1,
            font=ctk.CTkFont(size=FontSize.BUTTON),
        )
        self._back_button.grid(row=0, column=0, padx=(Spacing.NONE, Spacing.LG), sticky="w")  # type: ignore

        # Settings title
        title_label: ctk.CTkLabel = ctk.CTkLabel(
            master=header_frame,
            text=f"Configuration de {self._report_name}",
            font=ctk.CTkFont(size=FontSize.H3, weight="bold"),
        )
        title_label.grid(row=0, column=1, sticky="w")  # type: ignore

        # Main content scrollable frame
        content_frame: ctk.CTkScrollableFrame = ctk.CTkScrollableFrame(master=self)
        content_frame.grid(row=1, column=0, padx=Spacing.LG, pady=(Spacing.SM, Spacing.LG), sticky="nsew")  # type: ignore
        content_frame.grid_columnconfigure(index=0, weight=1)

        # Create settings based on report type
        if (
            "mensuelle" in self._report_name.lower()
            or "monthly" in self._report_name.lower()
        ):
            self._create_monthly_settings(parent=content_frame)
        else:
            self._create_generic_settings(parent=content_frame)

        # Bottom buttons frame
        buttons_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self, fg_color=Color.TRANSPARENT
        )
        buttons_frame.grid(row=2, column=0, padx=Spacing.LG, pady=(Spacing.NONE, Spacing.LG), sticky="ew")  # type: ignore
        buttons_frame.grid_columnconfigure(index=0, weight=1)

        # Save button
        self._save_button: ctk.CTkButton = ctk.CTkButton(
            master=buttons_frame,
            text="Sauvegarder la configuration",
            command=self._save_settings,
            height=40,
            font=ctk.CTkFont(size=FontSize.BUTTON, weight="bold"),
        )
        self._save_button.grid(row=0, column=1, padx=(Spacing.SM, Spacing.NONE), sticky="e")  # type: ignore

        # Cancel button - secondary style
        cancel_button: ctk.CTkButton = ctk.CTkButton(
            master=buttons_frame,
            text="Annuler",
            command=self._on_back,
            height=40,
            fg_color=Color.TRANSPARENT,
            border_width=1,
            font=ctk.CTkFont(size=FontSize.BUTTON),
        )
        cancel_button.grid(row=0, column=0, sticky="w")  # type: ignore

    def _create_monthly_settings(self, parent: Any) -> None:
        # Programs section
        programs_section: SettingsSection = SettingsSection(
            parent=parent,
            title="Configuration des programmes",
            description="Sélectionnez les programmes à inclure dans le rapport d'activité mensuelle",
        )
        programs_section.grid(row=0, column=0, padx=Spacing.SM, pady=Spacing.SM, sticky="ew")  # type: ignore

        # Create program checkboxes
        programs: list[str] = [
            "Programme Alpha",
            "Programme Bêta",
            "Programme Gamma",
            "Programme Delta",
            "Programme Epsilon",
        ]

        for idx, program in enumerate(programs):
            checkbox: ctk.CTkCheckBox = ctk.CTkCheckBox(
                master=programs_section.get_content_frame(),
                text=program,
                font=ctk.CTkFont(size=FontSize.BODY),
            )
            checkbox.grid(row=idx, column=0, padx=Spacing.LG, pady=Spacing.XS, sticky="w")  # type: ignore
            self._settings_widgets[f"program_{idx}"] = checkbox

    def _create_generic_settings(self, parent: Any) -> None:
        # General settings section
        general_section: SettingsSection = SettingsSection(
            parent=parent,
            title="Paramètres généraux",
            description="Configurez les options générales pour ce type de rapport",
        )
        general_section.grid(row=0, column=0, padx=Spacing.SM, pady=Spacing.SM, sticky="ew")  # type: ignore

        general_frame: ctk.CTkFrame = general_section.get_content_frame()
        general_frame.grid_columnconfigure(index=1, weight=1)

        # Output format
        format_label: ctk.CTkLabel = ctk.CTkLabel(
            master=general_frame,
            text="Format de sortie :",
            font=ctk.CTkFont(size=FontSize.LABEL),
        )
        format_label.grid(row=0, column=0, padx=(Spacing.LG, Spacing.SM), pady=Spacing.SM, sticky="w")  # type: ignore

        format_option: ctk.CTkOptionMenu = ctk.CTkOptionMenu(
            master=general_frame,
            values=["Excel (.xlsx)", "CSV (.csv)", "PDF (.pdf)"],
            font=ctk.CTkFont(size=FontSize.BODY),
        )
        format_option.grid(row=0, column=1, padx=(Spacing.SM, Spacing.LG), pady=Spacing.SM, sticky="w")  # type: ignore
        self._settings_widgets["output_format"] = format_option

        # Processing options section
        processing_section: SettingsSection = SettingsSection(
            parent=parent,
            title="Options de traitement",
            description="Configurez la manière dont les données doivent être traitées",
        )
        processing_section.grid(row=1, column=0, padx=Spacing.SM, pady=Spacing.SM, sticky="ew")  # type: ignore

        processing_frame: ctk.CTkFrame = processing_section.get_content_frame()

        # Validation checkbox
        validation_checkbox: ctk.CTkCheckBox = ctk.CTkCheckBox(
            master=processing_frame,
            text="Effectuer la validation des données avant le traitement",
            font=ctk.CTkFont(size=FontSize.BODY),
        )
        validation_checkbox.grid(row=0, column=0, padx=Spacing.LG, pady=Spacing.XS, sticky="w")  # type: ignore
        validation_checkbox.select()  # type: ignore
        self._settings_widgets["validate_data"] = validation_checkbox

        # Duplicate handling
        duplicates_checkbox: ctk.CTkCheckBox = ctk.CTkCheckBox(
            master=processing_frame,
            text="Supprimer les entrées en double",
            font=ctk.CTkFont(size=FontSize.BODY),
        )
        duplicates_checkbox.grid(row=1, column=0, padx=Spacing.LG, pady=Spacing.XS, sticky="w")  # type: ignore
        self._settings_widgets["remove_duplicates"] = duplicates_checkbox

    def _save_settings(self) -> None:
        # TODO: Implement actual settings saving logic
        # For now, just show a message and go back
        print(f"Sauvegarde de la configuration pour {self._report_name}")

        # Collect all settings values
        settings_values: dict[str, Any] = {}
        for key, widget in self._settings_widgets.items():
            if isinstance(widget, ctk.CTkCheckBox):
                settings_values[key] = widget.get()  # type: ignore
            elif isinstance(widget, ctk.CTkOptionMenu):
                settings_values[key] = widget.get()  # type: ignore

        print(f"Valeurs de configuration : {settings_values}")

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

        # Title
        title_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self,
            text=self._title,
            font=ctk.CTkFont(size=FontSize.LABEL, weight="bold"),
        )
        title_label.grid(row=0, column=0, padx=Spacing.LG, pady=(Spacing.LG, Spacing.XS), sticky="w")  # type: ignore

        # Description
        desc_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self,
            text=self._description,
            font=ctk.CTkFont(size=FontSize.CAPTION),
            text_color=Color.GRAY,
        )
        desc_label.grid(row=1, column=0, padx=Spacing.LG, pady=(Spacing.NONE, Spacing.SM), sticky="w")  # type: ignore

        # Content frame
        self._content_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self, fg_color=Color.TRANSPARENT
        )
        self._content_frame.grid(row=2, column=0, padx=Spacing.XS, pady=(Spacing.NONE, Spacing.LG), sticky="ew")  # type: ignore
        self._content_frame.grid_columnconfigure(index=0, weight=1)

    def get_content_frame(self) -> ctk.CTkFrame:
        return self._content_frame
