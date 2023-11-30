"""Base Number for Econet300."""
from dataclasses import dataclass
import logging

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import Limits
from .common import Econet300Api, EconetDataCoordinator
from .const import DOMAIN, SERVICE_API, SERVICE_COORDINATOR
from .entity import EconetEntity

_LOGGER = logging.getLogger(__name__)


@dataclass
class EconetNumberEntityDescription(NumberEntityDescription):
    """Describes Econet binary sensor entity."""


NUMBER_TYPES: tuple[EconetNumberEntityDescription, ...] = (
    EconetNumberEntityDescription(
        key="tempCOSet",
        name="Boiler set temperature",
        translation_key="tempCOSet",
        icon="mdi:thermometer",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_registry_visible_default=True,
        min_value=27,
        max_value=68,
        native_step=1,
    ),
    EconetNumberEntityDescription(
        key="tempCWUSet",
        name="HUW set temperature",
        icon="mdi:thermometer",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_registry_visible_default=True,
        min_value=20,
        max_value=55,
        native_step=1,
    ),
)


class EconetNumber(EconetEntity, NumberEntity):
    """Describes Econet binary sensor entity."""

    def __init__(
        self,
        description: EconetNumberEntityDescription,
        coordinator: EconetDataCoordinator,
        api: Econet300Api,
    ):
        """Initialize the EconetNumber entity."""
        super().__init__(description, coordinator, api)

    def _sync_state(self, value):
        """Sync state."""

        self._attr_native_value = value


        self._attr_native_min_value = value - 1
        self._attr_native_max_value = value + 1

        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        _LOGGER.debug("Set value: %s", value)

        if value == self._attr_native_value:
            return

        if value > self._attr_native_max_value:
            _LOGGER.warning(
                "Requested value: '%s' exceeds maximum allowed value: '%s'",
                value,
                self._attr_max_value,
            )

        if value < self._attr_native_min_value:
            _LOGGER.warning(
                "Requested value: '%s' is below allowed value: '%s'",
                value,
                self._attr_min_value,
            )
            return

        if not await self._api.set_param(self.entity_description.key, int(value)):
            _LOGGER.warning("Setting value failed")
            return

        self._attr_native_value = value
        self.async_write_ha_state()


def can_add(desc: EconetNumberEntityDescription, coordinator: EconetDataCoordinator):
    """Check if a given entity can be added based on the availability of data in the coordinator."""
    return coordinator.has_data(desc.key) and coordinator.data[desc.key]


def apply_limits(desc: EconetNumberEntityDescription, limits: Limits):
    """Set the native minimum and maximum values for the given entity description."""
    desc.native_min_value = limits.min
    desc.native_max_value = limits.max


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> bool:
    """Set up the sensor platform."""

    coordinator = hass.data[DOMAIN][entry.entry_id][SERVICE_COORDINATOR]
    api = hass.data[DOMAIN][entry.entry_id][SERVICE_API]

    entities: list[EconetNumber] = []

    for description in NUMBER_TYPES:
        number_limits = await api.get_param_limits(description.key)

        if number_limits is None:
            _LOGGER.warning(
                "Cannot add entity: {}, numeric limits for this entity is None"
            )
            continue

        if can_add(description, coordinator):
            apply_limits(description, number_limits)
            entities.append(EconetNumber(description, coordinator, api))
        else:
            _LOGGER.debug(
                "Cannot add entity - availability key: %s does not exist",
                description.key,
            )

    return async_add_entities(entities)
