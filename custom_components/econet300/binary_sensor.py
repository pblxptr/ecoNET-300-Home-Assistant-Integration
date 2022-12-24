from dataclasses import dataclass
from typing import Callable, Any

from homeassistant.components.binary_sensor import BinarySensorEntityDescription, BinarySensorDeviceClass, \
    BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .common import EconetDataCoordinator, Econet300Api

from .const import DOMAIN, SERVICE_COORDINATOR, SERVICE_API, DEVICE_INFO_NAME, DEVICE_INFO_MODEL, \
    DEVICE_INFO_MANUFACTURER

import logging

from .entity import EconetDeviceInfo, EconetEntity

_LOGGER = logging.getLogger(__name__)


@dataclass
class EconetBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes Econet binary sensor entity."""
    availability_key: str = ""


BINARY_SENSOR_TYPES: tuple[EconetBinarySensorEntityDescription, ...] = (
    EconetBinarySensorEntityDescription(
        availability_key="pumpCWU",
        key="pumpCWUWorks",
        name="Water pump",
        icon="mdi:pump",
        device_class=BinarySensorDeviceClass.RUNNING
    ),
    EconetBinarySensorEntityDescription(
        availability_key="pumpCirculation",
        key="pumpCirculationWorks",
        name="Circulation pump",
        icon="mdi:pump",
        device_class=BinarySensorDeviceClass.RUNNING
    ),
    EconetBinarySensorEntityDescription(
        availability_key="pumpFireplace",
        key="pumpFireplaceWorks",
        name="Fireplace pump",
        icon="mdi:pump",
        device_class=BinarySensorDeviceClass.RUNNING
    ),
    EconetBinarySensorEntityDescription(
        availability_key="pumpSolar",
        key="pumpSolarWorks",
        name="Solar pump",
        icon="mdi:pump",
        device_class=BinarySensorDeviceClass.RUNNING
    ),
    EconetBinarySensorEntityDescription(
        availability_key="lighter",
        key="lighterWorks",
        name="Lighter",
        icon="mdi:fire",
        device_class=BinarySensorDeviceClass.RUNNING
    )
)


class EconetBinarySensor(EconetEntity, BinarySensorEntity):
    """Describes Econet binary sensor entity."""

    def __init__(self, description: EconetBinarySensorEntityDescription, coordinator: EconetDataCoordinator,
                 device_info: EconetDeviceInfo):
        super().__init__(description, coordinator, device_info)

    def _sync_state(self, value):
        """Sync state"""

        self._attr_is_on = value
        self.async_write_ha_state()


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> bool:
    """Set up the sensor platform."""

    coordinator = hass.data[DOMAIN][entry.entry_id][SERVICE_COORDINATOR]
    api = hass.data[DOMAIN][entry.entry_id][SERVICE_API]

    uid = await api.uid()

    device_info = EconetDeviceInfo(
        uid=uid,
        identifiers={(tuple(uid))},
        name=DEVICE_INFO_NAME,
        manufacturer=DEVICE_INFO_MANUFACTURER,
        model=DEVICE_INFO_MODEL
    )

    entities: list[EconetBinarySensor] = []

    for description in BINARY_SENSOR_TYPES:
        if coordinator.has_data(description.availability_key) and \
                coordinator.data[description.availability_key] is not False:
            entities.append(EconetBinarySensor(description, coordinator, device_info))
        else:
            _LOGGER.debug("Availability key: " + description.availability_key + "does not exist, entity will not be "
                                                                                "added")

    return async_add_entities(entities)
