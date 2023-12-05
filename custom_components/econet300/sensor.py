"""Sensor for Econet300."""
from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .common import Econet300Api, EconetDataCoordinator
from .const import (
    AVAILABLE_NUMBER_OF_MIXERS,
    DOMAIN,
    OPERATION_MODE_NAMES,
    REG_PARAM_PRECICION,
    SERVICE_API,
    SERVICE_COORDINATOR,
)
from .entity import EconetEntity, MixerEntity

_LOGGER = logging.getLogger(__name__)


@dataclass
class EconetSensorEntityDescription(SensorEntityDescription):
    """Describes Econet sensor entity."""

    process_val: Callable[[Any], Any] = lambda x: x


SENSOR_TYPES: tuple[EconetSensorEntityDescription, ...] = (
    EconetSensorEntityDescription(
        key="fanPower",
        translation_key="fanPower",
        name="Fan output",
        icon="mdi:fan",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER_FACTOR,
        process_val=lambda x: round(x, 2),
    ),
    EconetSensorEntityDescription(
        key="tempCO",
        translation_key="tempCO",
        name="Boiler temperature",
        icon="mdi:thermometer-lines",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=REG_PARAM_PRECICION["tempCO"],
        process_val=lambda x: x,
    ),
    EconetSensorEntityDescription(
        key="tempCOSet",
        name="Boiler set temperature",
        translation_key="tempCOSet",
        icon="mdi:thermometer-chevron-up",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        process_val=lambda x: round(x, 2),
    ),
    EconetSensorEntityDescription(
        key="tempFeeder",
        translation_key="tempFeeder",
        name="Feeder temperature",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=REG_PARAM_PRECICION["tempFeeder"],
        process_val=lambda x: x,
    ),
    EconetSensorEntityDescription(
        key="tempFlueGas",
        translation_key="tempFlueGas",
        name="Flue gas temperature",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=REG_PARAM_PRECICION["tempFlueGas"],
        process_val=lambda x: x,
    ),
    EconetSensorEntityDescription(
        key="tempBack",
        translation_key="tempBack",
        name="Water back temperature ",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        process_val=lambda x: round(x, 2),
    ),
    EconetSensorEntityDescription(
        key="tempCWU",
        translation_key="tempCWU",
        name="HUW temperature",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=REG_PARAM_PRECICION["tempCWU"],
        process_val=lambda x: x,
    ),
   EconetSensorEntityDescription(
        key="tempCWUSet",
        translation_key="CWU_SET_TEMP",
        name="HUW set temperature",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=REG_PARAM_PRECICION["tempCWUSet"],
        process_val=lambda x: x,
    ),
    EconetSensorEntityDescription(
        key="tempExternalSensor",
        translation_key="tempExternalSensor",
        name="Outside temperature",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=REG_PARAM_PRECICION["tempExternalSensor"],
        process_val=lambda x: x,
    ),
    EconetSensorEntityDescription(
        key="boilerPower",
        translation_key="boilerPower",
        name="Boiler output",
        icon="mdi:gauge",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER_FACTOR,
        suggested_display_precision=REG_PARAM_PRECICION["boilerPower"],
        process_val=lambda x: x,
    ),
    EconetSensorEntityDescription(
        key="fuelLevel",
        translation_key="fuelLevel",
        name="Fuel level",
        icon="mdi:gas-station",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        process_val=lambda x: round(x, 1),
    ),
    EconetSensorEntityDescription(
        key="mode",
        translation_key="mode",
        name="Operation mode",
        icon="mdi:sync",
        device_class="DEVICE_CLASS_OPERATION_MODE",  # custom class for boiler status
        process_val=lambda x: OPERATION_MODE_NAMES.get(x, "Unknown"),
    ),
    EconetSensorEntityDescription(
        key="lambdaSet",
        translation_key="lambdaSet",
        name="Oxygen set level",
        icon="mdi:lambda",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        process_val=lambda x: x / 10,
    ),
    EconetSensorEntityDescription(
        key="lambdaLevel",
        translation_key="lambdaLevel",
        name="Oxygen level",
        icon="mdi:lambda",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        process_val=lambda x: x / 10,
    ),
    EconetSensorEntityDescription(
        key="thermostat",
        translation_key="thermostat",
        name="Boiler thermostat",
        icon="mdi:thermostat",
        process_val=lambda x: "ON"
        if str(x).strip() == "1"
        else ("OFF" if str(x).strip() == "0" else None),
    ),
    EconetSensorEntityDescription(
        key="lambdaStatus",
        translation_key="lambdaStatus",
        name="Lamda status",
        icon="mdi:lambda",
        process_val=lambda x: "STOP"
        if x == 0
        else ("START" if x == 1 else ("Working" if x == 2 else "Unknown")),
    ),
        EconetSensorEntityDescription(
        key="tempUpperBuffer",
        translation_key="tempUpperBuffer",
        name="Upper buffer temperature",
        icon="mdi:thermometer",
        entity_registry_visible_default=False,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=REG_PARAM_PRECICION["tempUpperBuffer"],
        process_val=lambda x: x,
    ),
    EconetSensorEntityDescription(
        key="signal",
        translation_key="signal",
        name="Signal strength",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    EconetSensorEntityDescription(
        key="quality",
        translation_key="quality",
        name="Signal quality",
        icon="mdi:signal",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    EconetSensorEntityDescription(
        key="softVer",
        name="Module ecoNET software version",
        device_class="econet_software_version",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    EconetSensorEntityDescription(
        key="moduleASoftVer",
        name="Module A version",
        device_class="module_a_software_version",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    EconetSensorEntityDescription(
        key="moduleBSoftVer",
        name="Module B version",
        device_class="Module_b_software_version",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    EconetSensorEntityDescription(
        key="modulePanelSoftVer",
        name="Module Panel version",
        icon="mdi:raspberry-pi",
        device_class="module_panel_software_version",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    EconetSensorEntityDescription(
        key="moduleLambdaSoftVer",
        name="Module Lambda version",
        device_class="module_lamda_software_version",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    EconetSensorEntityDescription(
        key="protocolType",  #  "em" or "gm3_pomp"
        name="Protocol",
        device_class="protocol_type",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    EconetSensorEntityDescription(
        key="controllerID",
        name="Controler name",
        device_class="controller_ID",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


class EconetSensor(SensorEntity):
    """Econet Sensor."""

    def __init__(self, entity_description, name, unique_id):
        """Initialize the sensor."""
        super().__init__(name=name, unique_id=unique_id)
        self.entity_description = entity_description
        self._attr_native_value = None

    def _sync_state(self, value):
        """Sync state."""
        _LOGGER.debug("Update EconetSensor entity: %s", self.entity_description.name)

        self._attr_native_value = self.entity_description.process_val(value)

        self.async_write_ha_state()


class ControllerSensor(EconetEntity, EconetSensor):
    """class controller."""

    def __init__(
        self,
        description: EconetSensorEntityDescription,
        coordinator: EconetDataCoordinator,
        api: Econet300Api,
    ):
        """Initialize a new instance of the EconetSensor class."""
        super().__init__(description, coordinator, api)


class MixerSensor(MixerEntity, EconetSensor):
    """Mixer sensor class."""

    def __init__(
            self,
            description: EconetSensorEntityDescription,
            coordinator: EconetDataCoordinator,
            api: Econet300Api,
            idx: int,
        ):
            """Initialize a new instance of the EconetSensor class."""
            super().__init__(description, coordinator, api, idx)


def can_add(desc: EconetSensorEntityDescription, coordinator: EconetDataCoordinator):
    """Check if it can add the key."""
    if desc.key not in coordinator.data:
        _LOGGER.debug("Key %s does not exist in coordinator.data", desc.key)
        return False
    return coordinator.has_data(desc.key) and coordinator.data[desc.key] is not None


def create_controller_sensors(coordinator: EconetDataCoordinator, api: Econet300Api):
    """Add key."""
    entities = []

    for description in SENSOR_TYPES:
        if can_add(description, coordinator):
            entities.append(ControllerSensor(description, coordinator, api))
        else:
            _LOGGER.debug(
                "Availability key: %s does not exist, entity will not be added",
                description.key,
            )

    return entities


def create_mixer_sensors(coordinator: EconetDataCoordinator, api: Econet300Api):
    """Create individual sensor descriptions for mixer sensors."""
    entities = []

    for i in range(1, AVAILABLE_NUMBER_OF_MIXERS + 1):
        description = EconetSensorEntityDescription(
            key=f"mixerTemp{i}",
            name=f"Mixer {i} temperature",
            icon="mdi:thermometer",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.TEMPERATURE,
            process_val=lambda x: round(x, 2),
        )
        if can_add(description, coordinator):
            entities.append(MixerSensor(description, coordinator, api, i))
        else:
            _LOGGER.debug(
                "Availability key: %s does not exist, entity will not be added",
                description.key,
            )
        description2 = EconetSensorEntityDescription(
            key=f"mixerSetTemp{i}",
            name=f"Mixer {i} set temperature",
            icon="mdi:thermometer",
            entity_registry_enabled_default=False,
            entity_registry_visible_default=False,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.TEMPERATURE,
            process_val=lambda x: round(x, 2),
        )

        if can_add(description2, coordinator):
            entities.append(MixerSensor(description2, coordinator, api, i))
        else:
            _LOGGER.debug(
                "Availability key: %s does not exist, entity will not be added",
                description2.key,
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

    entities: list[EconetSensor] = []
    entities = entities + create_controller_sensors(coordinator, api)
    entities = entities + create_mixer_sensors(coordinator, api)

    return async_add_entities(entities)
