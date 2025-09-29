# Standard library imports
from typing import Any, Final, Set, final, List, Dict
from logging import Logger
import copy

# Third-party imports
import pandas as pd

# Local application imports
from app.common.logging_setup import get_logger
from app.core.domain.models.notification import Notification
from app.core.domain.models.subprogram import Subprogram
from app.core.infrastructure.file_io.file_io_service import FileIOService


@final
class SubprogramRegistry(object):
    __slots__ = ()

    _logger: Final[Logger] = get_logger(__name__)
    _initialized: bool = False

    def __new__(cls) -> None:
        raise RuntimeError(
            f"{cls.__name__} is not intended to be instantiated. Use class methods"
        )

    @classmethod
    def initialize(cls, file_io_service: FileIOService) -> None:
        if cls._initialized:
            cls._logger.debug("Registry already initialized, skipping")
            return

        cls._logger.info("Initializing SubprogramRegistry")

        # Convert default subprograms to dict format for file creation
        default_subprograms_dict = cls._convert_subprograms_to_dict(
            cls._DEFAULT_SUBPROGRAMS
        )

        # Ensure file exists with defaults if not present
        file_io_service.ensure_custom_subprograms_file_exists(default_subprograms_dict)

        # Clear and start with defaults
        cls._SUBPROGRAMS.clear()
        cls._SUBPROGRAMS.extend(copy.deepcopy(cls._DEFAULT_SUBPROGRAMS))
        cls._logger.info(f"Loaded {len(cls._DEFAULT_SUBPROGRAMS)} default subprograms")

        # Load and apply overrides from file
        cls.load_and_override_from_file(file_io_service)

        cls._initialized = True
        cls._logger.info(
            f"Registry initialized with {len(cls._SUBPROGRAMS)} total subprograms"
        )

    @classmethod
    def _convert_subprograms_to_dict(
        cls, subprograms: List[Subprogram]
    ) -> List[Dict[str, Any]]:
        """Convert Subprogram objects to dictionary format for JSON serialization"""
        result: List[Dict[str, Any]] = []
        for subprogram in subprograms:
            notifications_dict: List[Dict[str, Any]] = []
            for notification in subprogram.notifications:
                notifications_dict.append(
                    {
                        "name": notification.name,
                        "database_aliases": notification.database_aliases,
                        "aid_count": notification.aid_count,
                        "aid_amount": notification.aid_amount,
                    }
                )

            result.append(
                {
                    "name": subprogram.name,
                    "database_alias": subprogram.database_alias,
                    "notifications": notifications_dict,
                }
            )
        return result

    @classmethod
    def load_and_override_from_file(cls, file_io_service: FileIOService) -> None:
        try:
            # Pass default subprograms dict to file_io_service
            default_subprograms_dict = cls._convert_subprograms_to_dict(
                cls._DEFAULT_SUBPROGRAMS
            )
            custom_data: List[Dict[str, Any]] = (
                file_io_service.load_additional_subprograms(default_subprograms_dict)
            )

            if not custom_data:
                cls._logger.info("No custom subprograms to load from file")
                return

            # Track which defaults have been overridden
            overridden_names: Set[str] = set()
            new_subprograms: List[Subprogram] = []

            for subprogram_data in custom_data:
                try:
                    notifications: List[Notification] = []
                    for notif_data in subprogram_data.get("notifications", []):
                        notification: Notification = Notification(**notif_data)
                        notifications.append(notification)

                    subprogram_dict = subprogram_data.copy()
                    subprogram_dict["notifications"] = notifications
                    subprogram: Subprogram = Subprogram(**subprogram_dict)

                    # Check if this overrides an existing default
                    existing_index = None
                    for i, existing in enumerate(cls._SUBPROGRAMS):
                        if existing.name == subprogram.name:
                            existing_index = i
                            break

                    if existing_index is not None:
                        # Override existing subprogram
                        cls._SUBPROGRAMS[existing_index] = subprogram
                        overridden_names.add(subprogram.name)
                        cls._logger.info(
                            f"Overriding default subprogram: {subprogram.name}"
                        )
                    else:
                        # Add as new subprogram
                        new_subprograms.append(subprogram)
                        cls._logger.info(
                            f"Adding new custom subprogram: {subprogram.name}"
                        )

                except Exception as error:
                    cls._logger.error(
                        f"Failed to parse custom subprogram {subprogram_data.get('name', 'unknown')}: {error}"
                    )

            # Add all new subprograms to registry
            cls._SUBPROGRAMS.extend(new_subprograms)

            if overridden_names:
                cls._logger.info(
                    f"Overrode {len(overridden_names)} default subprogram(s): {list(overridden_names)}"
                )

            if new_subprograms:
                cls._logger.info(
                    f"Added {len(new_subprograms)} new custom subprogram(s): "
                    f"{[s.name for s in new_subprograms]}"
                )

        except Exception as error:
            cls._logger.error(f"Failed to load custom subprograms: {error}")
            cls._logger.warning("Continuing with default subprograms only")

    @classmethod
    def get_subprogram(cls, subprogram_name: str) -> Subprogram:
        cls._logger.debug(f"Retrieving subprogram: {subprogram_name}")

        for subprogram in cls._SUBPROGRAMS:
            if subprogram.name == subprogram_name:
                cls._logger.info(
                    f"Retrieved subprogram '{subprogram_name}' with {len(subprogram.notifications)} notifications"
                )
                return subprogram

        available_names: List[str] = [
            subprogram.name for subprogram in cls._SUBPROGRAMS
        ]
        error_msg: str = (
            f"Subprogram '{subprogram_name}' not found. Available: {available_names}"
        )
        cls._logger.error(error_msg)
        raise ValueError(error_msg)

    @classmethod
    def get_subprogram_by_database_alias(cls, database_alias: str) -> Subprogram:
        cls._logger.debug(f"Retrieving subprogram by database alias: {database_alias}")

        for subprogram in cls._SUBPROGRAMS:
            if subprogram.database_alias == database_alias:
                cls._logger.info(
                    f"Retrieved subprogram '{subprogram.name}' by database alias '{database_alias}'"
                )
                return subprogram

        available_aliases: List[str] = [
            subprogram.database_alias for subprogram in cls._SUBPROGRAMS
        ]
        error_msg: str = (
            f"Subprogram with database alias '{database_alias}' not found. Available: {available_aliases}"
        )
        cls._logger.error(error_msg)
        raise ValueError(error_msg)

    @classmethod
    def has_subprogram(cls, subprogram_name: str) -> bool:
        cls._logger.debug(f"Checking existence of subprogram: {subprogram_name}")
        exists: bool = any(
            subprogram.name == subprogram_name for subprogram in cls._SUBPROGRAMS
        )
        cls._logger.debug(f"Subprogram '{subprogram_name}' exists: {exists}")
        return exists

    @classmethod
    def has_subprogram_by_database_alias(cls, database_alias: str) -> bool:
        cls._logger.debug(
            f"Checking existence of subprogram by database alias: {database_alias}"
        )
        exists: bool = any(
            subprogram.database_alias == database_alias
            for subprogram in cls._SUBPROGRAMS
        )
        cls._logger.debug(
            f"Subprogram with database alias '{database_alias}' exists: {exists}"
        )
        return exists

    @classmethod
    def get_all_subprograms(cls) -> List[Subprogram]:
        cls._logger.debug("Retrieving all subprograms")
        cls._logger.info(f"Retrieved {len(cls._SUBPROGRAMS)} subprograms")
        return list(cls._SUBPROGRAMS)

    @classmethod
    def get_all_subprogram_names(cls) -> List[str]:
        cls._logger.debug("Retrieving all subprogram names")
        cls._logger.info(f"Retrieved {len(cls._SUBPROGRAMS)} subprogram names")
        return [subprogram.name for subprogram in cls._SUBPROGRAMS]

    @classmethod
    def _get_all_default_subprograms(cls) -> List[Subprogram]:
        return copy.deepcopy(cls._DEFAULT_SUBPROGRAMS)

    @classmethod
    def get_notification(
        cls, subprogram_name: str, notification_name: str
    ) -> Notification:
        cls._logger.debug(
            f"Retrieving notification '{notification_name}' from subprogram '{subprogram_name}'"
        )

        subprogram: Subprogram = cls.get_subprogram(subprogram_name)
        for notification in subprogram.notifications:
            if notification.name == notification_name:
                cls._logger.info(
                    f"Retrieved notification '{notification_name}' from subprogram '{subprogram_name}'"
                )
                return notification

        available_notification_names: List[str] = [
            notification.name for notification in subprogram.notifications
        ]
        error_msg: str = (
            f"Notification '{notification_name}' not found in subprogram '{subprogram_name}'. "
            f"Available: {available_notification_names}"
        )
        cls._logger.error(error_msg)
        raise ValueError(error_msg)

    @classmethod
    def get_notification_by_database_alias(cls, database_alias: str) -> Notification:
        cls._logger.debug(
            f"Retrieving notification by database alias: {database_alias}"
        )

        for subprogram in cls._SUBPROGRAMS:
            for notification in subprogram.notifications:
                if database_alias in notification.database_aliases:
                    cls._logger.info(
                        f"Retrieved notification '{notification.name}' by database alias '{database_alias}'"
                    )
                    return notification

        error_msg: str = (
            f"Notification with database alias '{database_alias}' not found"
        )
        cls._logger.error(error_msg)
        raise ValueError(error_msg)

    @classmethod
    def has_notification(cls, subprogram_name: str, notification_name: str) -> bool:
        cls._logger.debug(
            f"Checking existence of notification '{notification_name}' in subprogram '{subprogram_name}'"
        )

        if not cls.has_subprogram(subprogram_name):
            return False

        subprogram: Subprogram = cls.get_subprogram(subprogram_name)
        exists: bool = any(
            notification.name == notification_name
            for notification in subprogram.notifications
        )
        cls._logger.debug(
            f"Notification '{notification_name}' exists in subprogram '{subprogram_name}': {exists}"
        )
        return exists

    @classmethod
    def get_all_notifications(cls) -> List[Notification]:
        cls._logger.debug("Retrieving all notifications")
        notifications: List[Notification] = [
            notification
            for subprogram in cls._SUBPROGRAMS
            for notification in subprogram.notifications
        ]
        cls._logger.info(f"Retrieved {len(notifications)} notifications")
        return notifications

    @classmethod
    def get_all_default_notifications(cls) -> List[Notification]:
        cls._logger.debug("Retrieving all notifications")
        notifications: List[Notification] = [
            notification
            for subprogram in cls._DEFAULT_SUBPROGRAMS
            for notification in subprogram.notifications
        ]
        cls._logger.info(f"Retrieved {len(notifications)} notifications")
        return notifications

    @classmethod
    def get_subprograms_dataframe(cls) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "subprogram": subprogram.database_alias,
                    "aid_count": sum(
                        notification.aid_count
                        for notification in subprogram.notifications
                    ),
                }
                for subprogram in cls._SUBPROGRAMS
            ]
        )

    @classmethod
    def reset_to_default(cls) -> None:
        cls._logger.debug("Resetting registry to default state")

        cls._SUBPROGRAMS.clear()
        cls._SUBPROGRAMS.extend(copy.deepcopy(cls._DEFAULT_SUBPROGRAMS))

        cls._logger.info(
            f"Registry reset to default state with {len(cls._DEFAULT_SUBPROGRAMS)} subprograms"
        )

    @classmethod
    def get_registry_statistics(cls) -> Dict[str, int]:
        total_subprograms: int = len(cls._SUBPROGRAMS)
        total_default_subprograms: int = len(cls._DEFAULT_SUBPROGRAMS)
        total_notifications: int = sum(
            len(subprogram.notifications) for subprogram in cls._SUBPROGRAMS
        )
        total_default_notifications: int = sum(
            len(subprogram.notifications) for subprogram in cls._DEFAULT_SUBPROGRAMS
        )

        # Count overrides and additions
        overrides = 0
        additions = 0
        default_names = {s.name for s in cls._DEFAULT_SUBPROGRAMS}

        for subprogram in cls._SUBPROGRAMS:
            if subprogram.name in default_names:
                # Check if it's actually modified
                default_subprogram = next(
                    (s for s in cls._DEFAULT_SUBPROGRAMS if s.name == subprogram.name),
                    None,
                )
                if default_subprogram and subprogram != default_subprogram:
                    overrides += 1
            else:
                additions += 1

        return {
            "total_subprograms": total_subprograms,
            "default_subprograms": total_default_subprograms,
            "overridden_subprograms": overrides,
            "additional_subprograms": additions,
            "total_notifications": total_notifications,
            "default_notifications": total_default_notifications,
        }

    ALL_NOTIFICATIONS_OBJECT: Notification = Notification(
        name="Toutes",
        database_aliases=[],
        aid_count=0,
        aid_amount=0,
    )

    _DEFAULT_SUBPROGRAMS: Final[List[Subprogram]] = [
        Subprogram(
            name="2002",
            database_alias="PROGRAMME 2002",
            notifications=[
                Notification(
                    name="N° 530 (500 000 DA)",
                    database_aliases=[
                        "N°: 530. Du: 06/08/2002. TRANCHE: 0. Montant:    700 000"
                    ],
                    aid_count=250,
                    aid_amount=500000,
                ),
                Notification(
                    name="N° 530 (250 000 DA)",
                    database_aliases=[
                        "N°: 530. Du: 06/08/2002. TRANCHE: 0. Montant:    250 000"
                    ],
                    aid_count=249,
                    aid_amount=250000,
                ),
            ],
        ),
        Subprogram(
            name="2003",
            database_alias="PROGRAMME 2003",
            notifications=[
                Notification(
                    name="N° 1082 (500 000 DA)",
                    database_aliases=[
                        "N°: 1082. Du: 25/01/2003. TRANCHE: 0. Montant:    700 000",
                    ],
                    aid_count=250,
                    aid_amount=500000,
                ),
                Notification(
                    name="N° 1082 (250 000 DA)",
                    database_aliases=[
                        "N°: 1082. Du: 25/01/2003. TRANCHE: 0. Montant:    250 000",
                    ],
                    aid_count=245,
                    aid_amount=250000,
                ),
                Notification(
                    name="N° 731",
                    database_aliases=[
                        "N°: 731. Du: 30/12/2003. TRANCHE: 0. Montant:    700 000"
                    ],
                    aid_count=1093,
                    aid_amount=700000,
                ),
                Notification(
                    name="N° 281",
                    database_aliases=[
                        "N°: 281. Du: 28/04/2003. TRANCHE: 0. Montant:    700 000"
                    ],
                    aid_count=479,
                    aid_amount=500000,
                ),
            ],
        ),
        Subprogram(
            name="2003 CEE",
            database_alias="PROGRAMME 2003 CEE",
            notifications=[
                Notification(
                    name="N° 284",
                    database_aliases=[
                        "N°:284.Du:28/04/2003.TRANCHE:0.Montant:   700 000",
                        "N°: 284. Du: 28/04/2003. TRANCHE: 0. Montant:    700 000",
                    ],
                    aid_count=200,
                    aid_amount=700000,
                ),
            ],
        ),
        Subprogram(
            name="2004",
            database_alias="PROGRAMME 2004",
            notifications=[
                Notification(
                    name="N° 430",
                    database_aliases=[
                        "N°: 430. Du: 03/08/2004. TRANCHE: 0. Montant:    700 000"
                    ],
                    aid_count=30,
                    aid_amount=700000,
                ),
            ],
        ),
        Subprogram(
            name="2005",
            database_alias="PROGRAMME INITIAL",
            notifications=[
                Notification(
                    name="N° 872",
                    database_aliases=[
                        "N°:872.Du:06/12/2004.TRANCHE:0.Montant:   700 000",
                        "N°: 872. Du: 06/12/2004. TRANCHE: 0. Montant:    700 000",
                    ],
                    aid_count=20000,
                    aid_amount=700000,
                ),
            ],
        ),
        Subprogram(
            name="Complémentaire 2007",
            database_alias="COMPLEMENTAIRE 2007",
            notifications=[
                Notification(
                    name="N° 568",
                    database_aliases=[
                        "N°: 568. Du: 20/05/2007. TRANCHE: 0. Montant:    700 000"
                    ],
                    aid_count=50,
                    aid_amount=700000,
                ),
            ],
        ),
        Subprogram(
            name="Rattrapage 2007",
            database_alias="PQR 2007",
            notifications=[
                Notification(
                    name="N° 592",
                    database_aliases=[
                        "N°:592.Du:26/05/2007.TRANCHE:0.Montant:   250 000",
                        "N°: 592. Du: 26/05/2007. TRANCHE: 0. Montant:    250 000",
                    ],
                    aid_count=888,
                    aid_amount=250000,
                ),
            ],
        ),
        Subprogram(
            name="Complémentaire 2008",
            database_alias="COMPLEMENTAIRE 2008",
            notifications=[
                Notification(
                    name="N° 738",
                    database_aliases=[
                        "N°: 738. Du: 20/07/2008. TRANCHE: 0. Montant:    700 000"
                    ],
                    aid_count=1000,
                    aid_amount=700000,
                ),
                Notification(
                    name="N° 1077",
                    database_aliases=[
                        "N°:1077.Du:14/08/2008.TRANCHE:1.Montant:   700 000",
                        "N°: 1077. Du: 14/08/2008. TRANCHE: 1. Montant:    700 000",
                    ],
                    aid_count=500,
                    aid_amount=700000,
                ),
            ],
        ),
        Subprogram(
            name="Complémentaire 2009",
            database_alias="COMPLEMENTAIRE 2009",
            notifications=[
                Notification(
                    name="N° 260",
                    database_aliases=[
                        "N°:260.Du:19/02/2009.TRANCHE:0.Montant:   700 000",
                        "N°: 260. Du: 19/02/2009. TRANCHE: 0. Montant:    700 000",
                    ],
                    aid_count=2000,
                    aid_amount=700000,
                ),
                Notification(
                    name="N° 852",
                    database_aliases=[
                        "N°:852.Du:13/04/2009.TRANCHE:0.Montant:   700 000",
                        "N°: 852. Du: 13/04/2009. TRANCHE: 0. Montant:    700 000",
                    ],
                    aid_count=1000,
                    aid_amount=700000,
                ),
                Notification(
                    name="N° 1037",
                    database_aliases=[
                        "N°:1037.Du:01/10/2009.TRANCHE:1.Montant:   700 000",
                        "N°: 1037. Du: 01/10/2009. TRANCHE: 1. Montant:    700 000",
                    ],
                    aid_count=1000,
                    aid_amount=700000,
                ),
            ],
        ),
        Subprogram(
            name="2010",
            database_alias=" QUINQUINNAL 2010",
            notifications=[
                Notification(
                    name="N° 250",
                    database_aliases=[
                        "N°:250.Du:23/03/2010.TRANCHE:0.Montant:   700 000",
                        "N°: 250. Du: 23/03/2010. TRANCHE: 0. Montant:    700 000",
                    ],
                    aid_count=3000,
                    aid_amount=700000,
                ),
                Notification(
                    name="N° 834",
                    database_aliases=[
                        "N°:834.Du:23/09/2010.TRANCHE:0.Montant:   700 000",
                        "N°: 834. Du: 23/09/2010. TRANCHE: 0. Montant:    700 000",
                    ],
                    aid_count=3500,
                    aid_amount=700000,
                ),
            ],
        ),
        Subprogram(
            name="2011",
            database_alias=" QUINQUENNAL 2011",
            notifications=[
                Notification(
                    name="N° 587",
                    database_aliases=[
                        "N°:587.Du:26/05/2016.TRANCHE:0.Montant:   700 000",
                        "N°: 587. Du: 26/05/2016. TRANCHE: 0. Montant:    700 000",
                    ],
                    aid_count=266,
                    aid_amount=700000,
                ),
                Notification(
                    name="N° 856",
                    database_aliases=[
                        "N°:856.Du:09/09/2017.TRANCHE:0.Montant:   700 000",
                        "N°: 856. Du: 09/09/2017. TRANCHE: 0. Montant:    700 000",
                    ],
                    aid_count=42,
                    aid_amount=700000,
                ),
            ],
        ),
        Subprogram(
            name="Complémentaire 2011",
            database_alias="QUINQUENNAL 2011C",
            notifications=[
                Notification(
                    name="N° 224",
                    database_aliases=[
                        "N°:224.Du:06/02/2011.TRANCHE:1.Montant:   700 000",
                        "N°: 224. Du: 06/02/2011. TRANCHE: 1. Montant:    700 000",
                    ],
                    aid_count=4500,
                    aid_amount=700000,
                ),
                Notification(
                    name="N° 463",
                    database_aliases=[
                        "N°:463.Du:03/03/2011.TRANCHE:1.Montant:   700 000",
                        "N°: 463. Du: 03/03/2011. TRANCHE: 1. Montant:    700 000",
                    ],
                    aid_count=11000,
                    aid_amount=700000,
                ),
                Notification(
                    name="N° 1161",
                    database_aliases=[
                        "N°:1161.Du:07/06/2011.TRANCHE:2.Montant:   700 000",
                        "N°: 1161. Du: 07/06/2011. TRANCHE: 2. Montant:    700 000",
                    ],
                    aid_count=5000,
                    aid_amount=700000,
                ),
            ],
        ),
        Subprogram(
            name="2013",
            database_alias="PQ2013",
            notifications=[
                Notification(
                    name="N° 1132",
                    database_aliases=[
                        "N°:1132.Du:16/07/2013.TRANCHE:2.Montant:   700 000",
                        "N°: 1132. Du: 16/07/2013. TRANCHE: 2. Montant:    700 000",
                    ],
                    aid_count=5000,
                    aid_amount=700000,
                ),
                Notification(
                    name="N° 587",
                    database_aliases=[
                        "N°:587.Du:26/05/2016.TRANCHE:0.Montant:   700 000",
                        "N°: 587. Du: 26/05/2016. TRANCHE: 0. Montant:    700 000",
                    ],
                    aid_count=481,
                    aid_amount=700000,
                ),
                Notification(
                    name="N° 856",
                    database_aliases=[
                        "N°:856.Du:09/09/2017.TRANCHE:0.Montant:   700 000",
                        "N°: 856. Du: 09/09/2017. TRANCHE: 0. Montant:    700 000",
                    ],
                    aid_count=37,
                    aid_amount=700000,
                ),
            ],
        ),
        Subprogram(
            name="Complémentaire 2013",
            database_alias="QUINQUENNAL 2013 C",
            notifications=[
                Notification(
                    name="N° 587",
                    database_aliases=[
                        "N°:587.Du:26/05/2016.TRANCHE:0.Montant:   700 000",
                        "N°: 587. Du: 26/05/2016. TRANCHE: 0. Montant:    700 000",
                    ],
                    aid_count=1253,
                    aid_amount=700000,
                ),
            ],
        ),
        Subprogram(
            name="2014",
            database_alias="PROGRAMME Q 2014",
            notifications=[
                Notification(
                    name="N° 460",
                    database_aliases=[
                        "N°:460.Du:05/03/2014.TRANCHE:0.Montant:   700 000",
                        "N°: 460. Du: 05/03/2014. TRANCHE: 0. Montant:    700 000",
                    ],
                    aid_count=8000,
                    aid_amount=700000,
                ),
            ],
        ),
        Subprogram(
            name="2015",
            database_alias="Programme 2015",
            notifications=[
                Notification(
                    name="N° 605",
                    database_aliases=[
                        "N°:605.Du:25/08/2015.TRANCHE:0.Montant:   700 000",
                        "N°: 605. Du: 25/08/2015. TRANCHE: 0. Montant:    700 000",
                    ],
                    aid_count=2040,
                    aid_amount=700000,
                ),
            ],
        ),
        Subprogram(
            name="Complémentaire 2015",
            database_alias="Complémentaire 2015",
            notifications=[
                Notification(
                    name="N° 838",
                    database_aliases=[
                        "N°:838.Du:10/11/2015.TRANCHE:0.Montant:   700 000",
                        "N°: 838. Du: 10/11/2015. TRANCHE: 0. Montant:    700 000",
                    ],
                    aid_count=3000,
                    aid_amount=700000,
                ),
            ],
        ),
        Subprogram(
            name="2016",
            database_alias="Programme 2016",
            notifications=[
                Notification(
                    name="N° 1024",
                    database_aliases=[
                        "N°:1024.Du:15/10/2017.TRANCHE:0.Montant:   700 000",
                        "N°: 1024. Du: 15/10/2017. TRANCHE: 0. Montant:    700 000",
                    ],
                    aid_count=1000,
                    aid_amount=700000,
                ),
                Notification(
                    name="N° 183",
                    database_aliases=[
                        "N°:183.Du:04/02/2018.TRANCHE:0.Montant:   700 000",
                        "N°: 183. Du: 04/02/2018. TRANCHE: 0. Montant:    700 000",
                    ],
                    aid_count=3000,
                    aid_amount=700000,
                ),
            ],
        ),
        Subprogram(
            name="2018",
            database_alias="Programme  2018",
            notifications=[
                Notification(
                    name="N° 241",
                    database_aliases=[
                        "N°:241.Du:12/02/2018.TRANCHE:0.Montant:   700 000",
                        "N°: 241. Du: 12/02/2018. TRANCHE: 0. Montant:    700 000",
                    ],
                    aid_count=3000,
                    aid_amount=700000,
                ),
                Notification(
                    name="N° 798",
                    database_aliases=[
                        "N°:798.Du:09/07/2018.TRANCHE:1.Montant:   700 000",
                        "N°: 798. Du: 09/07/2018. TRANCHE: 1. Montant:    700 000",
                    ],
                    aid_count=2000,
                    aid_amount=700000,
                ),
            ],
        ),
        Subprogram(
            name="2019",
            database_alias="Programme 2019",
            notifications=[
                Notification(
                    name="N° 245",
                    database_aliases=[
                        "N°:245.Du:03/02/2019.TRANCHE:0.Montant:   700 000",
                        "N°: 245. Du: 03/02/2019. TRANCHE: 0. Montant:    700 000",
                    ],
                    aid_count=2200,
                    aid_amount=700000,
                ),
                Notification(
                    name="N° 375",
                    database_aliases=[
                        "N°:375.Du:26/02/2019.TRANCHE:1.Montant:   700 000"
                    ],
                    aid_count=50,
                    aid_amount=700000,
                ),
            ],
        ),
        Subprogram(
            name="2020",
            database_alias="Programme 2020",
            notifications=[
                Notification(
                    name="N° 705",
                    database_aliases=[
                        "N°:705.Du:29/06/2020.TRANCHE:0.Montant:   700 000"
                    ],
                    aid_count=600,
                    aid_amount=700000,
                ),
                Notification(
                    name="N° 1350",
                    database_aliases=[
                        "N°:1350.Du:05/11/2020.TRANCHE:0.Montant:   700 000"
                    ],
                    aid_count=600,
                    aid_amount=700000,
                ),
            ],
        ),
        Subprogram(
            name="2021",
            database_alias="Programme 2021",
            notifications=[
                Notification(
                    name="N° 329",
                    database_aliases=[
                        "N°:329.Du:02/02/2021.TRANCHE:0.Montant:   700 000"
                    ],
                    aid_count=1500,
                    aid_amount=700000,
                ),
            ],
        ),
        Subprogram(
            name="2022",
            database_alias="programme 2022",
            notifications=[
                Notification(
                    name="N° 238",
                    database_aliases=[
                        "N°:238.Du:26/03/2022.TRANCHE:0.Montant:   700 000"
                    ],
                    aid_count=2500,
                    aid_amount=700000,
                ),
            ],
        ),
        Subprogram(
            name="2023",
            database_alias="programme 2023",
            notifications=[
                Notification(
                    name="N° 666",
                    database_aliases=[
                        "N°:666.Du:06/08/2023.TRANCHE:0.Montant:   700 000"
                    ],
                    aid_count=2000,
                    aid_amount=700000,
                ),
            ],
        ),
        Subprogram(
            name="2024",
            database_alias="Programme 2024",
            notifications=[
                Notification(
                    name="N° 1061",
                    database_aliases=[
                        "N°:1061.Du:14/12/2023.TRANCHE:0.Montant:   700 000",
                        "N°:1061.Du:14/12/2023.TRANCHE:1.Montant:   700 000",
                    ],
                    aid_count=1000,
                    aid_amount=700000,
                ),
                Notification(
                    name="N° 734",
                    database_aliases=[
                        "N°:734.Du:30/07/2024.TRANCHE:0.Montant:   700 000"
                    ],
                    aid_count=4000,
                    aid_amount=700000,
                ),
            ],
        ),
        Subprogram(
            name="2025",
            database_alias="PROGRAMME 2025",
            notifications=[
                Notification(
                    name="N° 16",
                    database_aliases=[
                        "N°:16.Du:06/01/2025.TRANCHE:0.Montant:   700 000"
                    ],
                    aid_count=1000,
                    aid_amount=700000,
                ),
            ],
        ),
    ]

    _SUBPROGRAMS: List[Subprogram] = copy.deepcopy(_DEFAULT_SUBPROGRAMS)
