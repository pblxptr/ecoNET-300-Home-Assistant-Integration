from dataclasses import dataclass

from config.custom_components.econet300.common import EconetDataCoordinator, Econet300Api
from homeassistant.components.sensor import SensorEntityDescription, SensorStateClass, SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_CELSIUS, PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, COORDINATOR_PROP_NAME, API_PROP_NAME, DEVICE_INFO_NAME, DEVICE_INFO_MODEL, \
    DEVICE_INFO_MANUFACTURER

import logging

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .entity import EconetDeviceInfo

_LOGGER = logging.getLogger(__name__)


@dataclass
class EconetSensorEntityDescription(SensorEntityDescription):
    """Describes Econet sensor entity."""


SENSOR_TYPES: tuple[EconetSensorEntityDescription, ...] = (
    EconetSensorEntityDescription(
        key="tempFeeder",
        name="Feeder temp",
        icon="mdi:thermometer",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    EconetSensorEntityDescription(
        key="fanPower",
        name="Fan power",
        icon="mdi:fan",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.SPEED,
    ),
    EconetSensorEntityDescription(
        key="tempFlueGas",
        name="Temp flue gas",
        icon="mdi:thermometer",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    EconetSensorEntityDescription(
        key="tempCO",
        name="Temp kettle",
        icon="mdi:thermometer",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    EconetSensorEntityDescription(
        key="tempBack",
        name="Temp back",
        icon="mdi:thermometer",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    EconetSensorEntityDescription(
        key="tempCWU",
        name="Temp CWU",
        icon="mdi:thermometer",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    EconetSensorEntityDescription(
        key="mixerTemp1",
        name="Temp Mixer 1",
        icon="mdi:thermometer",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    EconetSensorEntityDescription(
        key="mixerTemp2",
        name="Temp Mixer 2",
        icon="mdi:thermometer",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    EconetSensorEntityDescription(
        key="tempExternalSensor",
        name="Temp External Sensor",
        icon="mdi:thermometer",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    )
)


class EconetSensor(CoordinatorEntity, SensorEntity):
    """Describes Econet binary sensor entity."""

    def __init__(self, description: EconetSensorEntityDescription, coordinator: EconetDataCoordinator,
                 device_info: EconetDeviceInfo):
        super().__init__(coordinator)

        self.entity_description = description
        self._coordinator = coordinator

        self._attr_unique_id = f"{device_info['uid']}-{self.entity_description.key}"
        self._attr_device_info = device_info

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self.entity_description.name

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # self._attr_is_on = self.coordinator.data[self.idx]["state"]
        _LOGGER.debug("Update EconetSensor entity:" + self.entity_description.name)

        if self._coordinator.data[self.entity_description.key] is None:
            return

        self._attr_native_value = round(self._coordinator.data[self.entity_description.key], 2)

        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        return self._coordinator.data[self.entity_description.key] is not None


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> bool:
    """Set up the sensor platform."""

    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR_PROP_NAME]
    api = hass.data[DOMAIN][entry.entry_id][API_PROP_NAME]

    uid = await api.uid()

    device_info = EconetDeviceInfo(
        uid=uid,
        identifiers={(tuple(uid))},
        name=DEVICE_INFO_NAME,
        manufacturer=DEVICE_INFO_MANUFACTURER,
        model=DEVICE_INFO_MODEL
    )

    entities: list[EconetSensor] = [
        *[EconetSensor(description, coordinator, device_info) for description in SENSOR_TYPES]
    ]

    return async_add_entities(entities)
