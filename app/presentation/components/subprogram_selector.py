from __future__ import annotations

# Standard library imports
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.core.domain.predefined_objects.subprograms import SUBPROGRAMS
from app.presentation.components.base_component import BaseComponent
from app.presentation.styling.design_system import DesignSystem


class SubprogramSelector(BaseComponent):
    __slots__ = (
        "_on_selection_changed",
        "_subprogram_selector",
        "_notification_selector",
        "_selected_subprogram",
        "_selected_notification",
        "_selection_info_label",
        "_subprogram_var",
        "_notification_var",
    )

    def __init__(
        self,
        parent: Any,
        on_selection_changed: Callable[[str | None, str | None], None],
    ) -> None:
        self._on_selection_changed: Callable[[str | None, str | None], None] = (
            on_selection_changed
        )
        self._selected_subprogram: str | None = None
        self._selected_notification: str | None = None

        subprogram_names: list[str] = [subprogram.name for subprogram in SUBPROGRAMS]
        default_subprogram_name: str = subprogram_names[-1] if subprogram_names else ""
        self._subprogram_var: ctk.StringVar = ctk.StringVar(
            value=default_subprogram_name
        )
        self._notification_var: ctk.StringVar = ctk.StringVar(value="")

        self._selected_subprogram = (
            default_subprogram_name if subprogram_names else None
        )

        super().__init__(parent, "Sous-programme et notification")

    def _setup_content(self) -> None:
        self._content_frame.grid_columnconfigure(index=1, weight=1)
        self._content_frame.grid_columnconfigure(index=3, weight=1)

        title: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text=self._title,
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
            columnspan=4,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM),
            sticky="w",
        )

        information: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text="Sélectionnez le sous-programme et la notification pour lesquels vous souhaitez générer le rapport",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.CAPTION,
            ),
            text_color=DesignSystem.Color.GRAY,
        )
        information.grid(  # type: ignore
            row=1,
            column=0,
            columnspan=4,
            pady=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM),
            sticky="w",
        )

        # Subprogram selector
        subprogram_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text="Sous-programme :",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.BODY,
                weight="bold",
            ),
            text_color=DesignSystem.Color.BLACK,
            anchor="w",
        )
        subprogram_label.grid(  # type: ignore
            row=2,
            column=0,
            padx=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM),
            sticky="w",
        )

        subprogram_names: list[str] = [subprogram.name for subprogram in SUBPROGRAMS]
        self._subprogram_selector: ctk.CTkComboBox = ctk.CTkComboBox(
            master=self._content_frame,
            values=subprogram_names,
            variable=self._subprogram_var,
            command=lambda _: self._handle_subprogram_selection(),
            width=DesignSystem.Width.MD,
            height=DesignSystem.Height.SM,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL, size=DesignSystem.FontSize.BODY
            ),
            dropdown_font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL, size=DesignSystem.FontSize.BODY
            ),
            state="readonly",
            border_width=DesignSystem.BorderWidth.XS,
            corner_radius=DesignSystem.Roundness.SM,
        )
        self._subprogram_selector.grid(  # type: ignore
            row=2,
            column=1,
            padx=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.MD),
            sticky="ew",
        )

        # Notification selector
        notification_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text="Notification :",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL,
                size=DesignSystem.FontSize.BODY,
                weight="bold",
            ),
            text_color=DesignSystem.Color.BLACK,
            anchor="w",
        )
        notification_label.grid(  # type: ignore
            row=2,
            column=2,
            padx=(DesignSystem.Spacing.NONE, DesignSystem.Spacing.SM),
            sticky="w",
        )

        self._notification_selector: ctk.CTkComboBox = ctk.CTkComboBox(
            master=self._content_frame,
            values=[],
            variable=self._notification_var,
            command=lambda _: self._handle_notification_selection(),
            width=DesignSystem.Width.MD,
            height=DesignSystem.Height.SM,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL, size=DesignSystem.FontSize.BODY
            ),
            dropdown_font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL, size=DesignSystem.FontSize.BODY
            ),
            state="readonly",
            border_width=DesignSystem.BorderWidth.XS,
            corner_radius=DesignSystem.Roundness.SM,
        )
        self._notification_selector.grid(row=2, column=3, sticky="ew")  # type: ignore

        # Info display frame
        info_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self._content_frame,
            fg_color=DesignSystem.Color.LESS_WHITE,
            border_width=DesignSystem.BorderWidth.XS,
            border_color=DesignSystem.Color.LIGHTER_GRAY,
            corner_radius=DesignSystem.Roundness.SM,
        )
        info_frame.grid(  # type: ignore
            row=3,
            column=0,
            columnspan=4,
            pady=(DesignSystem.Spacing.MD, DesignSystem.Spacing.NONE),
            sticky="ew",
        )
        info_frame.grid_columnconfigure(index=0, weight=1)

        self._selection_info_label: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text=self._get_selection_info_text(),
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL, size=DesignSystem.FontSize.BODY
            ),
            text_color=DesignSystem.Color.BLACK,
            justify="left",
            anchor="nw",
        )
        self._selection_info_label.grid(  # type: ignore
            row=0,
            column=0,
            padx=DesignSystem.Spacing.MD,
            pady=DesignSystem.Spacing.MD,
            sticky="w",
        )

        # Initialize notification selector and trigger callback if subprogram exists
        if subprogram_names:
            self._handle_subprogram_selection()

    def _handle_subprogram_selection(self) -> None:
        self._selected_subprogram = self._subprogram_var.get()

        # Update notification selector based on selected subprogram
        notification_names: list[str] = []
        for subprogram in SUBPROGRAMS:
            if subprogram.name == self._selected_subprogram:
                notification_names = [
                    notification.name for notification in subprogram.notifications
                ]
                break

        self._notification_selector.configure(values=notification_names)  # type: ignore

        # Select first notification if available
        if notification_names:
            self._notification_var.set(notification_names[0])
            self._selected_notification = notification_names[0]
        else:
            self._notification_var.set("")
            self._selected_notification = None

        self._selection_info_label.configure(text=self._get_selection_info_text())  # type: ignore
        self._on_selection_changed(
            self._selected_subprogram, self._selected_notification
        )

    def _handle_notification_selection(self) -> None:
        self._selected_notification = self._notification_var.get()
        self._selection_info_label.configure(text=self._get_selection_info_text())  # type: ignore
        self._on_selection_changed(
            self._selected_subprogram, self._selected_notification
        )

    def _get_selection_info_text(self) -> str:
        if not self._selected_subprogram:
            return "Aucun sous-programme sélectionné"

        if not self._selected_notification:
            return f"Programme : {self._selected_subprogram}\nAucune notification sélectionnée"

        # Find the selected notification details
        for subprogram in SUBPROGRAMS:
            if subprogram.name == self._selected_subprogram:
                for notification in subprogram.notifications:
                    if notification.name == self._selected_notification:
                        formatted_amount: str = f"{notification.aid_amount:_}".replace(
                            "_", " "
                        )
                        return (
                            f"Sous-programme : {subprogram.name}\n"
                            f"Notification : {notification.name}\n"
                            f"Montant de l'aide : {formatted_amount} DA\n"
                            f"Consistance : {notification.aid_count}"
                        )
                break

        return "Information de la notification non disponible"

    def get_selected_subprogram(self) -> str | None:
        return self._selected_subprogram

    def get_selected_notification(self) -> str | None:
        return self._selected_notification

    def get_selection(self) -> tuple[str | None, str | None]:
        return self._selected_subprogram, self._selected_notification

    def reset_to_first(self) -> None:
        subprogram_names: list[str] = [subprogram.name for subprogram in SUBPROGRAMS]

        if subprogram_names:
            self._subprogram_var.set(subprogram_names[0])
            self._handle_subprogram_selection()
