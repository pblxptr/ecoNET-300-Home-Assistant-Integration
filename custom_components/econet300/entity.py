import logging
from dataclasses import dataclass

from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .common import EconetDataCoordinator

_LOGGER = logging.getLogger(__name__)


class EconetDeviceInfo(DeviceInfo):
    """EconetDeviceInfo"""
    uid: str


class EconetEntity(CoordinatorEntity):
    """Representes EconetEntity"""

    def __init__(self, description: EntityDescription, coordinator: EconetDataCoordinator,
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
        _LOGGER.debug("Update EconetEntity, entity name:" + self.entity_description.name)

        if self._coordinator.data[self.entity_description.key] is None:
            return

        value = self._coordinator.data[self.entity_description.key]

        self._sync_state(value)

    async def async_added_to_hass(self):
        """Handle added to hass."""
        _LOGGER.debug("Added to HASS:" + self.entity_description.name)

        if self._coordinator.data[self.entity_description.key] is None:
            _LOGGER.warning("Data key: " + self.entity_description.key + " was expected to exist but it doesn't")
            return

        value = self._coordinator.data[self.entity_description.key]

        await super().async_added_to_hass()
        self._sync_state(value)
