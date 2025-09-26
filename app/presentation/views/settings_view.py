from __future__ import annotations

# Standard library imports
from logging import Logger
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.presentation.styling.design_system import DesignSystem
from app.core.core_facade import CoreFacade
from app.common.logging_setup import get_logger


class SettingsView(ctk.CTkFrame):
    __slots__ = (
        "_logger",
        "_facade",
        "_on_back",
        "_current_subview",
        "_back_button",
        "_scrollable_frame",
    )

    def __init__(
        self,
        parent: Any,
        facade: CoreFacade,
        on_back: Callable[[], None],
    ) -> None:
        super().__init__(master=parent)  # type: ignore

        self._logger: Logger = get_logger(__name__)
        self._facade: CoreFacade = facade
        self._on_back: Callable[[], None] = on_back
        self._current_subview: ctk.CTkFrame | None = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        self.configure(  # type: ignore
            fg_color=DesignSystem.Color.LEAST_WHITE,
            corner_radius=DesignSystem.Roundness.MD,
            border_color=DesignSystem.Color.LIGHTER_GRAY,
            border_width=DesignSystem.BorderWidth.XS,
        )

        self.grid_columnconfigure(index=0, weight=1)
        self.grid_rowconfigure(index=1, weight=1)

        # Header with back button
        header_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self, fg_color=DesignSystem.Color.TRANSPARENT
        )
        header_frame.grid(row=0, column=0, padx=DesignSystem.Spacing.LG, pady=(DesignSystem.Spacing.LG, DesignSystem.Spacing.XS), sticky="ew")  # type: ignore
        header_frame.grid_columnconfigure(index=1, weight=1)

        self._back_button = ctk.CTkButton(
            master=header_frame,
            text="Retour",
            text_color=DesignSystem.Color.WHITE,
            fg_color=DesignSystem.Color.GRAY,
            hover_color=DesignSystem.Color.DARKER_GRAY,
            corner_radius=DesignSystem.Roundness.XS,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.BUTTON,
                weight="bold",
            ),
            command=self._on_back,
            width=DesignSystem.Width.SM,
            height=DesignSystem.Height.SM,
        )
        self._back_button.grid(row=0, column=0, padx=DesignSystem.Spacing.NONE, sticky="w")  # type: ignore

        info_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=header_frame, fg_color=DesignSystem.Color.TRANSPARENT
        )
        info_frame.grid(row=0, column=1, sticky="ew")  # type: ignore
        info_frame.grid_columnconfigure(index=0, weight=1)

        title_label: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text="Paramètres de l'application",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.H2,
                weight="bold",
            ),
            text_color=DesignSystem.Color.BLACK,
        )
        title_label.grid(row=0, column=0, padx=DesignSystem.Spacing.MD, pady=DesignSystem.Spacing.XS, sticky="w")  # type: ignore

        self._scrollable_frame = ctk.CTkScrollableFrame(
            master=self,
            fg_color=DesignSystem.Color.TRANSPARENT,
        )
        self._scrollable_frame.grid(  # type: ignore
            row=1,
            column=0,
            padx=DesignSystem.Spacing.XS,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.LG),
            sticky="nsew",
        )
        self._scrollable_frame.grid_columnconfigure(index=0, weight=1)

        self._show_settings()

    def _show_settings(self) -> None:
        description: ctk.CTkLabel = ctk.CTkLabel(
            master=self._scrollable_frame,
            text="Gérer les sous-programmes et notifications du système",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL, size=DesignSystem.FontSize.BODY
            ),
            text_color=DesignSystem.Color.DARKER_GRAY,
        )
        description.grid(  # type: ignore
            row=0,
            column=0,
            padx=DesignSystem.Spacing.SM,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.XL),
            sticky="w",
        )

        # Settings options container
        options_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self._scrollable_frame,
            fg_color=DesignSystem.Color.WHITE,
            corner_radius=DesignSystem.Roundness.MD,
            border_color=DesignSystem.Color.LIGHTER_GRAY,
            border_width=DesignSystem.BorderWidth.XS,
        )
        options_frame.grid(  # type: ignore
            row=1, column=0, pady=DesignSystem.Spacing.MD, sticky="ew"
        )
        options_frame.grid_columnconfigure(index=0, weight=1)

    def _create_option_card(
        self,
        parent: ctk.CTkFrame,
        title: str,
        description: str,
        button_text: str,
        on_click: Callable[[], None],
    ) -> ctk.CTkFrame:
        card: ctk.CTkFrame = ctk.CTkFrame(
            master=parent,
            fg_color=DesignSystem.Color.LEAST_WHITE,
            corner_radius=DesignSystem.Roundness.SM,
            border_color=DesignSystem.Color.GRAY,
            border_width=DesignSystem.BorderWidth.XS,
        )
        card.grid_columnconfigure(index=0, weight=1)

        title_label: ctk.CTkLabel = ctk.CTkLabel(
            master=card,
            text=title,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.H3,
                weight="bold",
            ),
            text_color=DesignSystem.Color.BLACK,
        )
        title_label.grid(  # type: ignore
            row=0,
            column=0,
            padx=DesignSystem.Spacing.MD,
            pady=(DesignSystem.Spacing.MD, DesignSystem.Spacing.XS),
            sticky="w",
        )

        desc_label: ctk.CTkLabel = ctk.CTkLabel(
            master=card,
            text=description,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.BODY,
            ),
            text_color=DesignSystem.Color.DARKER_GRAY,
        )
        desc_label.grid(  # type: ignore
            row=1,
            column=0,
            padx=DesignSystem.Spacing.MD,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM),
            sticky="w",
        )

        button: ctk.CTkButton = ctk.CTkButton(
            master=card,
            text=button_text,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.BODY,
                weight="bold",
            ),
            fg_color=DesignSystem.Color.BLACK,
            text_color=DesignSystem.Color.WHITE,
            hover_color=DesignSystem.Color.DARKER_GRAY,
            corner_radius=DesignSystem.Roundness.SM,
            height=36,
            width=100,
            command=on_click,
        )
        button.grid(  # type: ignore
            row=2,
            column=0,
            padx=DesignSystem.Spacing.MD,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.MD),
            sticky="e",
        )

        return card

    def _on_subprogram_added(self, subprogram_name: str) -> None:
        self._logger.info(f"Successfully added subprogram: {subprogram_name}")
        self._show_settings()

    def _on_notification_added(
        self, notification_name: str, subprogram_name: str
    ) -> None:
        self._logger.info(
            f"Successfully added notification '{notification_name}' to subprogram '{subprogram_name}'"
        )
        self._show_settings()
