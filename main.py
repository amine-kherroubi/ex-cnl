from __future__ import annotations

# Third-party imports
from customtkinter import CTk  # type: ignore

# Local application imports
from app.config import AppConfig
from app.utils.logging_setup import LoggingSetup
from app.application_facade import ApplicationFacade
from gui.main_window import MainWindow


def main() -> None:
    # Setup config and logging
    config: AppConfig = AppConfig()
    LoggingSetup.configure(config.logging_config)

    # Create facade
    facade: ApplicationFacade = ApplicationFacade(config)

    # Run GUI
    app: CTk = MainWindow(facade)
    app.mainloop()  # type: ignore


if __name__ == "__main__":
    main()
