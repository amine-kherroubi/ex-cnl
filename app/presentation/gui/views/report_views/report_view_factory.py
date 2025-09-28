# Standard library imports
from logging import Logger
from typing import Any, Callable, Optional, Type, final

# Local application imports
from app.common.logging_setup import get_logger
from app.core.domain.models.report_specification import ReportSpecification
from app.core.facade import CoreFacade
from app.presentation.gui.views.report_views.base_report_view import BaseReportView
from app.presentation.gui.views.report_views.concrete_report_views import *


@final
class ReportViewFactory(object):
    __slots__ = ()

    _logger: Logger = get_logger(__name__)

    def __new__(cls) -> None:
        raise RuntimeError(
            f"{cls.__name__} is not intended to be instantiated. Use class methods"
        )

    @classmethod
    def create_view(
        cls,
        parent: Any,
        report_spec: ReportSpecification,
        core_facade: CoreFacade,
        on_back: Callable[[], None],
    ) -> BaseReportView:
        cls._logger.info(f"Creating view for report: {report_spec.name}")
        cls._logger.debug(f"Available views: {list(views.keys())}")

        view: Optional[Type[BaseReportView]] = views.get(report_spec.name)
        if view is None:
            error_msg: str = f"Unknown report: {report_spec.name}"
            cls._logger.error(f"{error_msg}. Available: {list(views.keys())}")
            raise ValueError(error_msg)

        cls._logger.info(
            f"{view.__name__} created successfully for report '{report_spec.name}'"
        )

        return view(
            parent=parent,
            report_spec=report_spec,
            core_facade=core_facade,
            on_back=on_back,
        )
