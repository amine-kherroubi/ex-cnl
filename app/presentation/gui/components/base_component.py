

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
            fg_color=DesignSystem.Color.WHITE.value,
            border_width=DesignSystem.BorderWidth.XS.value,
            border_color=DesignSystem.Color.LIGHTER_GRAY.value,
            corner_radius=DesignSystem.Roundness.MD.value,
        )
        self.grid(row=0, column=0, padx=DesignSystem.Spacing.LG.value, pady=DesignSystem.Spacing.LG.value, sticky="ew")  # type: ignore

        self.grid_columnconfigure(index=0, weight=1)

        self._content_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self, fg_color=DesignSystem.Color.TRANSPARENT.value
        )
        self._content_frame.grid(row=0, column=0, padx=DesignSystem.Spacing.LG.value, pady=DesignSystem.Spacing.LG.value, sticky="ew")  # type: ignore

    @abstractmethod
    def _setup_content(self) -> None: ...
