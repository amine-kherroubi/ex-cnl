from __future__ import annotations

# Standard library imports
from typing import Any

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.core.domain.models.report_specification import (
    ReportSpecification,
    RequiredFile,
)
from app.presentation.components.base_component import BaseComponent
from app.presentation.styling.design_system import DesignSystem


class RequiredFilesComponent(BaseComponent):
    """Component displaying required files and their patterns for a report."""

    __slots__ = ("_report_spec",)

    def __init__(
        self,
        parent: Any,
        report_spec: ReportSpecification,
    ) -> None:
        self._report_spec: ReportSpecification = report_spec
        super().__init__(parent, "Fichiers requis")

    def _setup_content(self) -> None:
        """Set up the required files content."""
        # Configure grid
        self._content_frame.grid_columnconfigure(index=0, weight=1)

        # Title
        title: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text="Fichiers requis",
            text_color=DesignSystem.Color.BLACK,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.H3,
                weight="bold",
            ),
            anchor="w",
        )
        title.grid(  # type: ignore
            row=0,
            column=0,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM),
            sticky="w",
        )  # type: ignore

        # Required files list
        self._create_required_files_list()

        information: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text="La génération de ce rapport nécessite les fichiers Excel ci-dessus",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.CAPTION,
            ),
            text_color=DesignSystem.Color.GRAY,
        )
        information.grid(  # type: ignore
            row=1,
            column=0,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM),
            sticky="w",
        )

    def _create_required_files_list(self) -> None:
        """Create the list of required files with their patterns."""
        files_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self._content_frame,
            fg_color=DesignSystem.Color.TRANSPARENT,
        )
        files_frame.grid(  # type: ignore
            row=2,
            column=0,
            sticky="ew",
        )  # type: ignore
        files_frame.grid_columnconfigure(index=0, weight=1)

        row_index = 0
        for rf in self._report_spec.required_files:
            self._create_file_entry(files_frame, rf, row_index)
            row_index += 1

    def _create_file_entry(
        self, parent: ctk.CTkFrame, required_file: RequiredFile, row: int
    ) -> None:
        """Create a single file entry showing the pattern and table name."""
        # Entry frame with subtle background
        entry_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=parent,
            fg_color=DesignSystem.Color.LEAST_WHITE,
            border_width=DesignSystem.BorderWidth.XS,
            border_color=DesignSystem.Color.LIGHTER_GRAY,
            corner_radius=DesignSystem.Roundness.SM,
        )
        entry_frame.grid(  # type: ignore
            row=row,
            column=0,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.XS),
            sticky="ew",
        )  # type: ignore
        entry_frame.grid_columnconfigure(index=0, weight=1)

        # File pattern (main identifier)
        name: ctk.CTkLabel = ctk.CTkLabel(
            master=entry_frame,
            text=f"{required_file.name}",
            text_color=DesignSystem.Color.BLACK,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.BODY,
                weight="bold",
            ),
            anchor="w",
        )
        name.grid(  # type: ignore
            row=0,
            column=0,
            padx=DesignSystem.Spacing.SM,
            pady=(DesignSystem.Spacing.SM, DesignSystem.Spacing.NONE),
            sticky="w",
        )  # type: ignore

        # Table name (what it maps to)
        pattern: ctk.CTkLabel = ctk.CTkLabel(
            master=entry_frame,
            text=f"Doit respecter la forme : {required_file.readable_pattern}",
            text_color=DesignSystem.Color.DARKER_GRAY,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.CAPTION,
            ),
            anchor="w",
        )
        pattern.grid(  # type: ignore
            row=1,
            column=0,
            padx=DesignSystem.Spacing.SM,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM),
            sticky="w",
        )  # type: ignore
