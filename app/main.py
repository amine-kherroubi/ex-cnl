from __future__ import annotations
import sys
from app.application_facade import ApplicationFacade
from utils.config import ApplicationConfig
from utils.exceptions import ApplicationError


def main() -> None:
    config: ApplicationConfig = ApplicationConfig()

    try:
        app_facade: ApplicationFacade = ApplicationFacade(config)
        app_facade.run()

        sys.exit(0)

    except ApplicationError:
        sys.exit(1)
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()
