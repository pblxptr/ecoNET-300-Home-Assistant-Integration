"""Econet binary sensor."""
from dataclasses import dataclass
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .common import Econet300Api, EconetDataCoordinator
from .const import AVAILABLE_NUMBER_OF_MIXERS, DOMAIN, SERVICE_API, SERVICE_COORDINATOR
from .entity import EconetEntity, MixerEntity

_LOGGER = logging.getLogger(__name__)


@dataclass
class EconetBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes Econet binary sensor entity."""

    icon_off: str | None = None
    availability_key: str = ""


BINARY_SENSOR_TYPES: tuple[EconetBinarySensorEntityDescription, ...] = (
    EconetBinarySensorEntityDescription(
        availability_key="pumpCWU",
        key="pumpCWUWorks",
        translation_key="pumpCWU",
        name="HUW pump",
        icon="mdi:pump",
        icon_off="mdi:pump-off",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    EconetBinarySensorEntityDescription(
        availability_key="pumpCirculation",
        key="pumpCirculationWorks",
        translation_key="pumpCirculation",
        icon="mdi:pump",
        icon_off="mdi:pump-off",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    EconetBinarySensorEntityDescription(
        availability_key="pumpFireplace",
        key="pumpFireplaceWorks",
        name="Fireplace pump",
        icon="mdi:pump",
        icon_off="mdi:pump-off",
        device_class=BinarySensorDeviceClass.RUNNING,
        entity_registry_visible_default=False,
    ),
    EconetBinarySensorEntityDescription(
        availability_key="pumpSolar",
        key="pumpSolarWorks",
        name="Solar pump",
        icon="mdi:pump",
        icon_off="mdi:pump-off",
        device_class=BinarySensorDeviceClass.RUNNING,
        entity_registry_visible_default=False,
    ),
    EconetBinarySensorEntityDescription(
        availability_key="pumpCO",
        key="pumpCOWorks",
        name="Boiler pump",
        icon="mdi:pump",
        icon_off="mdi:pump-off",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    EconetBinarySensorEntityDescription(
        availability_key="lighter",
        key="lighterWorks",
        name="Lighter",
        icon="mdi:fire",
        icon_off="mdi:fire-off",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    EconetBinarySensorEntityDescription(
        availability_key="feeder",
        key="feederWorks",
        name="Feeder",
        icon="mdi:screw-lag",
        icon_off="mdi:screw-lag",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    EconetBinarySensorEntityDescription(
        availability_key="fan",
        key="fanWorks",
        name="Fan",
        icon="mdi:fan",
        icon_off="mdi:fan-off",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    EconetBinarySensorEntityDescription(
        availability_key="fan2Exhaust",
        key="fan2ExhaustWorks",
        name="Fan2",
        icon="mdi:fan",
        icon_off="mdi:fan-off",
        device_class=BinarySensorDeviceClass.RUNNING,
        entity_registry_visible_default=False,
    ),
)


class EconetBinarySensor(BinarySensorEntity):
    """Describe Econet Binary Sensor."""

    def _sync_state(self, value):
        """Sync state."""

        self._attr_is_on = value
        self.async_write_ha_state()

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend."""
        return (
            self.entity_description.icon_off
            if self.entity_description.icon_off is not None and not self.is_on
            else self.entity_description.icon
        )


class ControllerBinarySensor(EconetEntity, EconetBinarySensor):
    """Describes Econet binary sensor entity."""

    def __init__(
        self,
        description: EconetBinarySensorEntityDescription,
        coordinator: EconetDataCoordinator,
        api: Econet300Api,
    ):
        """Initialize the ControllerBinarySensor."""
        super().__init__(description, coordinator, api)


class MixerBinarySensor(MixerEntity, EconetBinarySensor):
    """Describes Econet Mixer binary sensor entity."""

    def __init__(
        self,
        description: EconetBinarySensorEntityDescription,
        coordinator: EconetDataCoordinator,
        api: Econet300Api,
        idx: int,
    ):
        """Initialize the MixerBinarySensor object with a description, coordinator, api, and index."""

        super().__init__(description, coordinator, api, idx)


def can_add(
    desc: EconetBinarySensorEntityDescription, coordinator: EconetDataCoordinator
):
    """Check can add key."""
    return (
        coordinator.has_data(desc.availability_key)
        and coordinator.data[desc.availability_key] is not False
    )


def can_add_mixer(
    desc: str, coordinator: EconetDataCoordinator
):
    return (
        coordinator.has_data(desc)
        and coordinator.data[desc] is not None
    )


def create_binary_sensors(coordinator: EconetDataCoordinator, api: Econet300Api):
    """Create binary sensors."""
    entities = []
    for description in BINARY_SENSOR_TYPES:
        if can_add(description, coordinator):
            entities.append(ControllerBinarySensor(description, coordinator, api))
        else:
            _LOGGER.debug(
                "Availability key: %s does not exist, entity will not be added.",
                description.key,
            )
    return entities


def create_mixer_sensors(coordinator: EconetDataCoordinator, api: Econet300Api):
    entities = []

    for i in range(1, AVAILABLE_NUMBER_OF_MIXERS + 1):
        availaimility_mixer_key = f"mixerTemp{i}"
        if can_add_mixer(availaimility_mixer_key, coordinator):
            description = EconetBinarySensorEntityDescription(
                availability_key=availaimility_mixer_key,
                key=f"mixerPumpWorks{i}",
                name=f"Mixer {i} pump works",
                icon="mdi:pump",
                device_class=BinarySensorDeviceClass.RUNNING,
            )

            entities.append(MixerBinarySensor(description, coordinator, api, i))
        else:
            _LOGGER.debug(
                "Availability key: %s does not exist, entity will not be added",
                description.key,
            )

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
