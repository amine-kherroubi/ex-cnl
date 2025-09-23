from __future__ import annotations

# Third-party imports
from customtkinter import CTk  # type: ignore

# Local application imports
from app.core.config import AppConfig
from app.core.utils.logging_setup import LoggingSetup
from app.core.core_facade import CoreFacade
from app.presentation.gui.windows.main_window import MainWindow


def main() -> None:
    # Setup config and logging
    config: AppConfig = AppConfig()
    LoggingSetup.configure(config.logging_config)

    # Create facade
    facade: CoreFacade = CoreFacade(config)

    # Run GUI
    app: CTk = MainWindow(facade)
    app.mainloop()  # type: ignore


if __name__ == "__main__":
    main()
