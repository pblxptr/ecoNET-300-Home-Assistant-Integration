from dataclasses import dataclass
from typing import Callable, Any

from homeassistant.components.number import NumberEntity, NumberDeviceClass, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .common import EconetDataCoordinator, Econet300Api, Limits

from .const import DOMAIN, SERVICE_COORDINATOR, SERVICE_API

import logging

from .entity import EconetDeviceInfo, EconetEntity, make_device_info

_LOGGER = logging.getLogger(__name__)


@dataclass
class EconetNumberEntityDescription(NumberEntityDescription):
    """Describes Econet binary sensor entity."""


NUMBER_TYPES: tuple[EconetNumberEntityDescription, ...] = (
    EconetNumberEntityDescription(
        key="tempCOSet",
        name="Temp CO set",
        icon="mdi:thermometer",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS
    ),
    EconetNumberEntityDescription(
        key="tempCWUSet",
        name="Temp CWU set",
        icon="mdi:thermometer",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS
    )
)


class EconetNumber(EconetEntity, NumberEntity):
    """Describes Econet binary sensor entity."""

    def __init__(self,
                 description: EconetNumberEntityDescription,
                 coordinator: EconetDataCoordinator,
                 device_info: EconetDeviceInfo,
                 limits: Limits
                 ):
        super().__init__(description, coordinator, device_info)

        self._attr_native_min_value = limits.min
        self._attr_native_max_value: limits.max

    def _sync_state(self, value):
        """Sync state"""

        self._attr_native_value = value
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        _LOGGER.debug("Set value: {}".format(value))

        self._attr_native_value = value
        self.async_write_ha_state()


def can_add(desc: EconetNumberEntityDescription, coordinator: EconetDataCoordinator):
    return coordinator.has_data(desc.key) and coordinator.data[desc.key]


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

    entities: list[EconetNumber] = []

    for description in NUMBER_TYPES:
        number_limits = await api.get_param_limits(description.key)

        if number_limits is None:
            _LOGGER.warning("Cannot add entity: {}, Numeric limits for this entity is None")
            continue

        if can_add(description, coordinator):
            entities.append(EconetNumber(description, coordinator, device_info, number_limits))
        else:
            _LOGGER.debug("Cannot add entity - availability key: {} does not exist".format(description.key))

    return async_add_entities(entities)
