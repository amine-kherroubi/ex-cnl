

# Standard library imports
from typing import Any, Callable

# Third-party imports
import customtkinter as ctk  # type: ignore

# Local application imports
from app.core.domain.registries.subprogram_registry import SubprogramRegistry
from app.core.domain.models.subprogram import Subprogram
from app.core.domain.models.notification import Notification
from app.presentation.gui.components.base_component import BaseComponent
from app.presentation.gui.styling.design_system import DesignSystem


class SubprogramSelector(BaseComponent):
    __slots__ = (
        "_on_selection_changed",
        "_subprogram_selector",
        "_notification_selector",
        "_selected_subprogram",
        "_selected_notification",
        "_current_possible_notifications",
        "_selection_info_label",
        "_subprogram_var",
        "_notification_var",
    )

    def __init__(
        self,
        parent: Any,
        on_selection_changed: Callable[[Subprogram, Notification], None],
    ) -> None:
        self._on_selection_changed: Callable[[Subprogram, Notification], None] = (
            on_selection_changed
        )
        self._selected_subprogram: Subprogram = (
            SubprogramRegistry.get_all_subprograms()[-1]
        )
        self._subprogram_var: ctk.StringVar = ctk.StringVar(
            value=self._selected_subprogram.name
        )

        self._selected_notification: Notification = (
            self._selected_subprogram.notifications[-1]
        )
        self._notification_var: ctk.StringVar = ctk.StringVar(
            value=self._selected_notification.name
        )

        super().__init__(parent, "Sous-programme et notification")

    def _setup_content(self) -> None:
        self._content_frame.grid_columnconfigure(index=1, weight=1)
        self._content_frame.grid_columnconfigure(index=3, weight=1)

        title: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text=self._title,
            text_color=DesignSystem.Color.BLACK.value,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value,
                size=DesignSystem.FontSize.H3.value,
                weight="bold",
            ),
            anchor="w",
        )
        title.grid(  # type: ignore
            row=0,
            column=0,
            columnspan=4,
            pady=(DesignSystem.Spacing.NONE.value, DesignSystem.Spacing.SM.value),
            sticky="w",
        )

        information: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text="Sélectionnez le sous-programme et la notification pour lesquels vous souhaitez générer le rapport",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value,
                size=DesignSystem.FontSize.CAPTION.value,
            ),
            text_color=DesignSystem.Color.GRAY.value,
        )
        information.grid(  # type: ignore
            row=1,
            column=0,
            columnspan=4,
            pady=(DesignSystem.Spacing.NONE.value, DesignSystem.Spacing.SM.value),
            sticky="w",
        )

        subprogram_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text="Sous-programme :",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value,
                size=DesignSystem.FontSize.BODY.value,
                weight="bold",
            ),
            text_color=DesignSystem.Color.BLACK.value,
            anchor="w",
        )
        subprogram_label.grid(  # type: ignore
            row=2,
            column=0,
            padx=(DesignSystem.Spacing.NONE.value, DesignSystem.Spacing.SM.value),
            sticky="w",
        )

        subprogram_names: list[str] = [
            subprogram.name for subprogram in SubprogramRegistry.get_all_subprograms()
        ]
        self._subprogram_selector: ctk.CTkComboBox = ctk.CTkComboBox(
            master=self._content_frame,
            values=subprogram_names,
            variable=self._subprogram_var,
            command=lambda _: self._handle_subprogram_selection(),
            width=DesignSystem.Width.MD.value,
            height=DesignSystem.Height.SM.value,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value, size=DesignSystem.FontSize.BODY.value
            ),
            dropdown_font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value, size=DesignSystem.FontSize.BODY.value
            ),
            state="readonly",
            border_width=DesignSystem.BorderWidth.XS.value,
            corner_radius=DesignSystem.Roundness.SM.value,
        )
        self._subprogram_selector.grid(  # type: ignore
            row=2,
            column=1,
            padx=(DesignSystem.Spacing.NONE.value, DesignSystem.Spacing.MD.value),
            sticky="ew",
        )

        notification_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self._content_frame,
            text="Notification :",
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value,
                size=DesignSystem.FontSize.BODY.value,
                weight="bold",
            ),
            text_color=DesignSystem.Color.BLACK.value,
            anchor="w",
        )
        notification_label.grid(  # type: ignore
            row=2,
            column=2,
            padx=(DesignSystem.Spacing.NONE.value, DesignSystem.Spacing.SM.value),
            sticky="w",
        )

        self._current_possible_notifications: list[Notification] = [
            notification for notification in self._selected_subprogram.notifications
        ]
        if len(self._selected_subprogram.notifications) > 1:
            self._current_possible_notifications.insert(
                0, SubprogramRegistry.ALL_NOTIFICATIONS_OBJECT
            )

        current_notification_names: list[str] = [
            notification.name for notification in self._current_possible_notifications
        ]
        self._notification_selector: ctk.CTkComboBox = ctk.CTkComboBox(
            master=self._content_frame,
            values=current_notification_names,
            variable=self._notification_var,
            command=lambda _: self._handle_notification_selection(),
            width=DesignSystem.Width.MD.value,
            height=DesignSystem.Height.SM.value,
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value, size=DesignSystem.FontSize.BODY.value
            ),
            dropdown_font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value, size=DesignSystem.FontSize.BODY.value
            ),
            state="readonly",
            border_width=DesignSystem.BorderWidth.XS.value,
            corner_radius=DesignSystem.Roundness.SM.value,
        )
        self._notification_selector.grid(row=2, column=3, sticky="ew")  # type: ignore

        info_frame: ctk.CTkFrame = ctk.CTkFrame(
            master=self._content_frame,
            fg_color=DesignSystem.Color.LESS_WHITE.value,
            border_width=DesignSystem.BorderWidth.XS.value,
            border_color=DesignSystem.Color.LIGHTER_GRAY.value,
            corner_radius=DesignSystem.Roundness.SM.value,
        )
        info_frame.grid(  # type: ignore
            row=3,
            column=0,
            columnspan=4,
            pady=(DesignSystem.Spacing.MD.value, DesignSystem.Spacing.NONE.value),
            sticky="ew",
        )
        info_frame.grid_columnconfigure(index=0, weight=1)

        self._selection_info_label: ctk.CTkLabel = ctk.CTkLabel(
            master=info_frame,
            text=self._get_selection_info_text(),
            font=ctk.CTkFont(
                family=DesignSystem.FontFamily.NORMAL.value, size=DesignSystem.FontSize.BODY.value
            ),
            text_color=DesignSystem.Color.BLACK.value,
            justify="left",
            anchor="nw",
        )
        self._selection_info_label.grid(  # type: ignore
            row=0,
            column=0,
            padx=DesignSystem.Spacing.MD.value,
            pady=DesignSystem.Spacing.MD.value,
            sticky="w",
        )

    def _handle_subprogram_selection(self) -> None:
        selected_subprogram_name: str = self._subprogram_var.get()

        for subprogram in SubprogramRegistry.get_all_subprograms():
            if subprogram.name == selected_subprogram_name:
                self._selected_subprogram = subprogram
                break

        self._current_possible_notifications = [
            notification for notification in self._selected_subprogram.notifications
        ]

        if len(self._selected_subprogram.notifications) > 1:
            self._current_possible_notifications.insert(
                0, SubprogramRegistry.ALL_NOTIFICATIONS_OBJECT
            )

        current_notification_names: list[str] = [
            notification.name for notification in self._current_possible_notifications
        ]

        self._notification_selector.configure(values=current_notification_names)  # type: ignore

        self._notification_var.set(self._current_possible_notifications[-1].name)
        self._selected_notification = self._current_possible_notifications[-1]

        self._selection_info_label.configure(text=self._get_selection_info_text())  # type: ignore
        self._on_selection_changed(
            self._selected_subprogram, self._selected_notification
        )

    def _handle_notification_selection(self) -> None:
        selected_notification_name: str = self._notification_var.get()
        for notification in self._current_possible_notifications:
            if notification.name == selected_notification_name:
                self._selected_notification = notification

        self._selection_info_label.configure(text=self._get_selection_info_text())  # type: ignore
        self._on_selection_changed(
            self._selected_subprogram, self._selected_notification
        )

    def _get_selection_info_text(self) -> str:
        if self._selected_notification == SubprogramRegistry.ALL_NOTIFICATIONS_OBJECT:
            notification_details: list[str] = []
            for notification in self._selected_subprogram.notifications:
                formatted_amount: str = f"{notification.aid_amount:_}".replace("_", " ")
                notification_details.append(
                    f"{notification.name} : {formatted_amount} DA ({notification.aid_count} aides)"
                )

            notifications_text: str = "\n".join(notification_details)

            return (
                f"Sous-programme : {self._selected_subprogram.name}\n"
                f"Notifications :\n{notifications_text}"
            )

        formatted_amount: str = f"{self._selected_notification.aid_amount:_}".replace(
            "_", " "
        )
        return (
            f"Sous-programme : {self._selected_subprogram.name}\n"
            f"Notification : {self._selected_notification.name}\n"
            f"Montant de l'aide : {formatted_amount} DA\n"
            f"Consistance : {self._selected_notification.aid_count}"
        )
