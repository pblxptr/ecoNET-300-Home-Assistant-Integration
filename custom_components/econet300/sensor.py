from dataclasses import dataclass
from typing import Callable, Any

from .common import EconetDataCoordinator, Econet300Api
from homeassistant.components.sensor import SensorEntityDescription, SensorStateClass, SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_CELSIUS, PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, SERVICE_COORDINATOR, SERVICE_API

import logging

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .entity import EconetDeviceInfo, EconetEntity, make_device_info

_LOGGER = logging.getLogger(__name__)


@dataclass
class EconetSensorEntityDescription(SensorEntityDescription):
    """Describes Econet sensor entity."""

    process_val: Callable[[Any], Any] = lambda x: x


SENSOR_TYPES: tuple[EconetSensorEntityDescription, ...] = (
    EconetSensorEntityDescription(
        key="tempFeeder",
        name="Feeder temp",
        icon="mdi:thermometer",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        process_val=lambda x: round(x, 2)
    ),
    EconetSensorEntityDescription(
        key="fanPower",
        name="Fan power",
        icon="mdi:fan",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.SPEED,
        process_val=lambda x: round(x, 2)
    ),
    EconetSensorEntityDescription(
        key="tempFlueGas",
        name="Exhaust temperature",
        icon="mdi:thermometer",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        process_val=lambda x: round(x, 2)
    ),
    EconetSensorEntityDescription(
        key="tempCO",
        name="Fireplace temperature",
        icon="mdi:thermometer",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        process_val=lambda x: round(x, 2)
    ),
    EconetSensorEntityDescription(
        key="tempBack",
        name="Water back temperature ",
        icon="mdi:thermometer",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        process_val=lambda x: round(x, 2)
    ),
    EconetSensorEntityDescription(
        key="tempCWU",
        name="Water temperature",
        icon="mdi:thermometer",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        process_val=lambda x: round(x, 2)
    ),
    EconetSensorEntityDescription(
        key="tempExternalSensor",
        name="Outside temperature",
        icon="mdi:thermometer",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        process_val=lambda x: round(x, 2)
    )
)


class EconetSensor(SensorEntity, EconetEntity):
    """Describes Econet binary sensor entity."""

    def __init__(self, description: EconetSensorEntityDescription, coordinator: EconetDataCoordinator,
                 device_info: EconetDeviceInfo):
        super().__init__(description, coordinator, device_info)

    def _sync_state(self, value):
        """Sync state"""
        _LOGGER.debug("Update EconetSensor entity:" + self.entity_description.name)

        self._attr_native_value = self.entity_description.process_val(value)

        self.async_write_ha_state()


def can_add(desc: EconetSensorEntityDescription, coordinator: EconetDataCoordinator):
    return coordinator.has_data(desc.key) and coordinator.data[desc.key] is not None


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> bool:
    """Set up the sensor platform."""

    coordinator = hass.data[DOMAIN][entry.entry_id][SERVICE_COORDINATOR]
    api = hass.data[DOMAIN][entry.entry_id][SERVICE_API]

    uid = await api.uid()

    device_info = make_device_info(uid, api.host())

    entities: list[EconetSensor] = []

    for description in SENSOR_TYPES:
        if can_add(description, coordinator):
            entities.append(EconetSensor(description, coordinator, device_info))
        else:
            _LOGGER.debug("Availability key: " + description.key + " does not exist, entity will not be "
                                                                   "added")
    return async_add_entities(entities)
