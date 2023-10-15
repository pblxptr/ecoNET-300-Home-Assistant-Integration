from abc import ABC
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
from .entity import EconetEntity

_LOGGER = logging.getLogger(__name__)


@dataclass
class EconetSensorEntityDescription(SensorEntityDescription):
    """Describes Econet sensor entity."""

    process_val: Callable[[Any], Any] = lambda x: x


SENSOR_TYPES: tuple[EconetSensorEntityDescription, ...] = (
        
    EconetSensorEntityDescription(
        key="fanPower",
        name="Fan power",
        icon="mdi:fan",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER_FACTOR,
        process_val=lambda x: round(x, 2)
    ),
    EconetSensorEntityDescription(
        key="tempCO",
        name="Boiler actual temp.",
        icon="mdi:thermometer-lines",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        process_val=lambda x: round(x, 2)
    ),
    EconetSensorEntityDescription(
        key="tempCOSet",
        name="Boiler set temp.",
        icon="mdi:thermometer-chevron-up",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        process_val=lambda x: round(x, 2)
    ),
    EconetSensorEntityDescription(
        key="tempFeeder",
        name="Feeder temp.",
        icon="mdi:thermometer",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
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
        key="mixerSetTemp1",
        name="Mixer 1 set temp.",
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
    ),
    EconetSensorEntityDescription(
        key="boilerPower",
        name="Boiler output",
        icon="mdi:gauge",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER_FACTOR,
        process_val=lambda x: round(x, 2)
    ),
    EconetSensorEntityDescription(
        key="fuelLevel",
        name="Fuel level",
        icon="mdi:gas-station",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        process_val=lambda x: round(x, 1)
    ),
    EconetSensorEntityDescription(
        key="mode",
        name="Operation mode",
        icon="mdi:sync",
        state_class=SensorStateClass.MEASUREMENT,
        process_val=lambda x: x
    ),
        EconetSensorEntityDescription(
        key="lambdaSet",
        name="Oxygen set level",
        icon="mdi:lambda",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        process_val=lambda x: x/10
    ),
        EconetSensorEntityDescription(
        key="lambdaLevel",
        name="Oxygen level",
        icon="mdi:lambda",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        process_val=lambda x: x/10
    )
)


class EconetSensor(SensorEntity):
    """"""

    def _sync_state(self, value):
        """Sync state"""
        _LOGGER.debug("Update EconetSensor entity:" + self.entity_description.name)

        self._attr_native_value = self.entity_description.process_val(value)

        self.async_write_ha_state()


class ControllerSensor(EconetEntity, EconetSensor):
    """"""

    def __init__(self, description: EconetSensorEntityDescription, coordinator: EconetDataCoordinator,
                api: Econet300Api):
        super().__init__(description, coordinator, api)


def can_add(desc: EconetSensorEntityDescription, coordinator: EconetDataCoordinator):
    return coordinator.has_data(desc.key) and coordinator.data[desc.key] is not None


def create_controller_sensors(coordinator: EconetDataCoordinator, api: Econet300Api):
    entities = []

    for description in SENSOR_TYPES:
        if can_add(description, coordinator):
            entities.append(ControllerSensor(description, coordinator, api))
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

    entities: list[EconetSensor] = []
    entities = entities + create_controller_sensors(coordinator, api)

    return async_add_entities(entities)
