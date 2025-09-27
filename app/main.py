from __future__ import annotations

# Third-party imports
from customtkinter import CTk  # type: ignore

# Local application imports
from app.config import AppConfig
from app.common.logging_setup import LoggingSetup
from app.core.facade import CoreFacade
from app.presentation.gui.windows.main_window import MainWindow


def main() -> None:
    config: AppConfig = AppConfig()
    LoggingSetup.configure(config.logging_config)

    core_facade: CoreFacade = CoreFacade(config)

    app: CTk = MainWindow(core_facade)
    app.mainloop()  # type: ignore


if __name__ == "__main__":
    main()
