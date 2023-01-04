from dataclasses import dataclass
from typing import Callable, Any

from homeassistant.components.binary_sensor import BinarySensorEntityDescription, BinarySensorDeviceClass, \
    BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .common import EconetDataCoordinator, Econet300Api

from .const import DOMAIN, SERVICE_COORDINATOR, SERVICE_API, DEVICE_INFO_CONTROLLER_NAME, DEVICE_INFO_MODEL, \
    DEVICE_INFO_MANUFACTURER, AVAILABLE_NUMBER_OF_MIXERS

import logging

from .entity import EconetEntity, MixerEntity

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


class EconetBinarySensor(BinarySensorEntity):
    """Describe Econet Binary Sensor"""

    def _sync_state(self, value):
        """Sync state"""

        self._attr_is_on = value
        self.async_write_ha_state()


class ControllerBinarySensor(EconetEntity, EconetBinarySensor):
    """Describes Econet binary sensor entity."""

    def __init__(self, description: EconetBinarySensorEntityDescription, coordinator: EconetDataCoordinator,
                 api: Econet300Api):
        super().__init__(description, coordinator, api)


class MixerBinarySensor(MixerEntity, EconetBinarySensor):
    """Describes Econet binary sensor entity."""

    def __init__(self, description: EconetBinarySensorEntityDescription, coordinator: EconetDataCoordinator,
                 api: Econet300Api, idx: int):
        super().__init__(description, coordinator, api, idx)


def can_add(desc: EconetBinarySensorEntityDescription, coordinator: EconetDataCoordinator):
    return coordinator.has_data(desc.availability_key) and coordinator.data[desc.availability_key] is not False


def can_add_mixer(desc: EconetBinarySensorEntityDescription, coordinator: EconetDataCoordinator):
    return coordinator.has_data(desc.availability_key) and coordinator.data[desc.availability_key] is not None


def create_binary_sensors(coordinator: EconetDataCoordinator, api: Econet300Api):
    entities = []
    for description in BINARY_SENSOR_TYPES:
        if can_add(description, coordinator):
            entities.append(ControllerBinarySensor(description, coordinator, api))
        else:
            _LOGGER.debug("Availability key: " + description.key + " does not exist, entity will not be "
                                                                   "added")

    return entities


def create_mixer_sensors(coordinator: EconetDataCoordinator, api: Econet300Api):
    entities = []

    for i in range(1, AVAILABLE_NUMBER_OF_MIXERS + 1):
        description = EconetBinarySensorEntityDescription(
            availability_key="mixerTemp{}".format(i),
            key="mixerPumpWorks{}".format(i),
            name="Mixer {} pump works".format(i),
            icon="mdi:pump",
            device_class=BinarySensorDeviceClass.RUNNING
        )

        if can_add_mixer(description, coordinator):
            entities.append(MixerBinarySensor(description, coordinator, api, i))
        else:
            _LOGGER.debug("Availability key: " + description.key + " does not exist, entity will not be "
                                                                   "added")

    return entities


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> bool:
    """Set up the sensor platform."""

    coordinator = hass.data[DOMAIN][entry.entry_id][SERVICE_COORDINATOR]
    api = hass.data[DOMAIN][entry.entry_id][SERVICE_API]

    entities: list[ControllerBinarySensor] = []
    entities = entities + create_binary_sensors(coordinator, api)
    entities = entities + create_mixer_sensors(coordinator, api)

    return async_add_entities(entities)
