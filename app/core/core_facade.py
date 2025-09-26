from __future__ import annotations

# Standard library imports
from logging import Logger
from pathlib import Path
from typing import Any

# Local application imports
from app.config import AppConfig
from app.core.domain.models.notification import Notification
from app.core.domain.models.report_context import ReportContext
from app.core.domain.models.report_specification import ReportSpecification
from app.core.domain.models.subprogram import Subprogram
from app.core.domain.registries.report_specification_registry import (
    ReportSpecificationRegistry,
)
from app.core.domain.registries.subprogram_registry import SubprogramRegistry
from app.core.infrastructure.data.data_repository import DuckDBRepository
from app.core.infrastructure.file_io.file_io_service import FileIOService
from app.core.services.report_generation_service.factories.report_generator_factory import (
    ReportGeneratorFactory,
)
from app.core.services.report_generation_service.base_generator import BaseGenerator
from app.common.logging_setup import get_logger


class CoreFacade(object):
    __slots__ = (
        "_config",
        "_data_repository",
        "_file_io_service",
        "_logger",
    )

    def __init__(self, config: AppConfig) -> None:
        self._logger: Logger = get_logger(__name__)
        self._logger.debug("Initializing CoreFacade")

        self._config: AppConfig = config
        self._data_repository: DuckDBRepository = DuckDBRepository(
            self._config.database_config
        )
        self._file_io_service: FileIOService = FileIOService(
            self._config.file_io_config
        )

        self._logger.info("CoreFacade initialized successfully")

    def generate_report(
        self,
        report_name: str,
        source_file_paths: dict[str, Path],
        output_directory_path: Path,
        report_context: ReportContext,
        **kwargs: Any,
    ) -> Path:
        self._logger.info(f"Starting report generation: {report_name}")

        try:
            report_specification: ReportSpecification = ReportSpecificationRegistry.get(
                report_name
            )
            self._logger.info(f"Generating report: {report_specification.display_name}")
            self._logger.debug(f"Report category: {report_specification.category}")

            generator: BaseGenerator = ReportGeneratorFactory.create_generator(
                report_name=report_name,
                file_io_service=self._file_io_service,
                data_repository=self._data_repository,
                report_context=report_context,
                **kwargs,
            )
            self._logger.debug(f"Generator created: {generator.__class__.__name__}")

            self._logger.info("Starting report generation process")
            output_file_path: Path = generator.generate(
                source_file_paths=source_file_paths,
                output_directory_path=output_directory_path,
            )

            self._logger.info(f"Report generated successfully: {output_file_path}")
            print(f"Report generated successfully: {output_file_path}")

            return output_file_path

        except ValueError as e:
            self._logger.error(f"Configuration error: {e}")
            raise
        except Exception as e:
            self._logger.exception(f"Unexpected error during report generation: {e}")
            raise

    def get_available_reports(self) -> dict[str, ReportSpecification]:
        self._logger.debug("Retrieving available reports")
        reports: dict[str, ReportSpecification] = ReportSpecificationRegistry.all()
        self._logger.info(f"Found {len(reports)} available report types")
        return reports

    def create_new_subprogram(self, subprogram: Subprogram) -> None:
        self._logger.debug(f"Creating new subprogram: {subprogram}")
        SubprogramRegistry.register_subprogram(subprogram)
        self._logger.info(f"New subprogram {subprogram.name} created successfully")

    def update_subprogram(
        self, subprogram_name: str, updated_subprogram: Subprogram
    ) -> None:
        self._logger.debug(f"Updating subprogram: {subprogram_name}")
        SubprogramRegistry.update_subprogram(subprogram_name, updated_subprogram)
        self._logger.info(f"Subprogram {subprogram_name} updated successfully")

    def delete_subprogram(self, subprogram_name: str) -> None:
        self._logger.debug(f"Deleting subprogram: {subprogram_name}")
        SubprogramRegistry.unregister_subprogram(subprogram_name)
        self._logger.info(f"Subprogram {subprogram_name} deleted successfully")

    def get_all_subprograms(self) -> list[Subprogram]:
        self._logger.debug("Retrieving all subprograms")
        subprograms: list[Subprogram] = SubprogramRegistry.get_all_subprograms()
        self._logger.info(f"Retrieved {len(subprograms)} subprograms")
        return subprograms

    def create_new_notification(
        self, subprogram_name: str, notification: Notification
    ) -> None:
        self._logger.debug(
            f"Creating new notification for subprogram {subprogram_name}: {notification}"
        )
        SubprogramRegistry.register_notification(subprogram_name, notification)
        self._logger.info(
            f"New notification {notification.name} for subprogram {subprogram_name} created successfully"
        )

    def update_notification(
        self,
        subprogram_name: str,
        notification_name: str,
        updated_notification: Notification,
    ) -> None:
        self._logger.debug(
            f"Updating notification {notification_name} in subprogram {subprogram_name}"
        )
        SubprogramRegistry.update_notification(
            subprogram_name, notification_name, updated_notification
        )
        self._logger.info(
            f"Notification {notification_name} in subprogram {subprogram_name} updated successfully"
        )

    def delete_notification(self, subprogram_name: str, notification_name: str) -> None:
        self._logger.debug(
            f"Deleting notification {notification_name} from subprogram {subprogram_name}"
        )
        SubprogramRegistry.unregister_notification(subprogram_name, notification_name)
        self._logger.info(
            f"Notification {notification_name} from subprogram {subprogram_name} deleted successfully"
        )

    def get_all_notifications(self) -> list[Notification]:
        self._logger.debug("Retrieving all notifications")
        notifications: list[Notification] = SubprogramRegistry.get_all_notifications()
        self._logger.info(f"Retrieved {len(notifications)} notifications")
        return notifications

    def reset_subprogram_registry(self) -> None:
        self._logger.debug("Resetting subprogram registry to default state")
        SubprogramRegistry.reset_to_default()
        self._logger.info("Subprogram registry reset to default state successfully")

    def get_subprogram_registry_status(self) -> dict[str, int]:
        self._logger.debug("Getting subprogram registry status")
        subprograms: list[Subprogram] = SubprogramRegistry.get_all_subprograms()
        notifications: list[Notification] = SubprogramRegistry.get_all_notifications()

        status: dict[str, int] = {
            "total_subprograms": len(subprograms),
            "total_notifications": len(notifications),
        }

        self._logger.info(f"Registry status: {status}")
        return status
