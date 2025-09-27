from __future__ import annotations

# Standard library imports
from abc import ABC, abstractmethod
from typing import Any

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.presentation.gui.styling.design_system import DesignSystem


class BaseComponent(ctk.CTkFrame, ABC):

    __slots__ = ("_content_frame", "_title")

    def __init__(self, parent: Any, title: str) -> None:
        super().__init__(master=parent)  # type: ignore

        self._title: str = title
        self._setup_base_ui()
        self._setup_content()

    def _setup_base_ui(self) -> None:

        self.configure(  # type: ignore
            fg_color=DesignSystem.Color.WHITE,
            border_width=DesignSystem.BorderWidth.XS,
            border_color=DesignSystem.Color.LIGHTER_GRAY,
            corner_radius=DesignSystem.Roundness.MD,
        )
        self.grid(row=0, column=0, padx=DesignSystem.Spacing.LG, pady=DesignSystem.Spacing.LG, sticky="ew")  # type: ignore

        self.grid_columnconfigure(index=0, weight=1)

        self._content_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self, fg_color=DesignSystem.Color.TRANSPARENT
        )
        self._content_frame.grid(row=0, column=0, padx=DesignSystem.Spacing.LG, pady=DesignSystem.Spacing.LG, sticky="ew")  # type: ignore

    @abstractmethod
    def _setup_content(self) -> None: ...
