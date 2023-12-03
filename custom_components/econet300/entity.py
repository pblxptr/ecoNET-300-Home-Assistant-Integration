"""Base econet entity class."""
import logging

from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import Econet300Api
from .common import EconetDataCoordinator
from .const import (
    DEVICE_INFO_CONTROLLER_NAME,
    DEVICE_INFO_MANUFACTURER,
    DEVICE_INFO_MIXER_NAME,
    DEVICE_INFO_MODEL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class EconetEntity(CoordinatorEntity):
    """Representes EconetEntity."""

    def __init__(
        self,
        description: EntityDescription,
        coordinator: EconetDataCoordinator,
        api: Econet300Api,
    ):
        super().__init__(coordinator)

        self.entity_description = description

        self._api = api
        self._coordinator = coordinator

    @property
    def unique_id(self) -> str | None:
        """Return the unique_id of the entity."""
        return f"{self._api.uid()}-{self.entity_description.key}"

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device info of the entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._api.uid())},
            name=DEVICE_INFO_CONTROLLER_NAME,
            manufacturer=DEVICE_INFO_MANUFACTURER,
            model=DEVICE_INFO_MODEL,
            configuration_url=self._api.host(),
            sw_version=self._api.sw_rev(),
            hw_version=self._api.hw_ver(),
        )

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self.entity_description.name

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug(
            "Update EconetEntity, entity name: %s", self.entity_description.name
        )

        if self._coordinator.data[self.entity_description.key] is None:
            return

        value = self._coordinator.data[self.entity_description.key]

        self._sync_state(value)

    async def async_added_to_hass(self):
        """Handle added to hass."""
        _LOGGER.debug("Added to HASS: %s", self.entity_description.name)

        if self._coordinator.data[self.entity_description.key] is None:
            _LOGGER.warning(
                "Data key: %s was expected to exist but it doesn't",
                self.entity_description.key,
            )

            return

        value = self._coordinator.data[self.entity_description.key]

        await super().async_added_to_hass()
        self._sync_state(value)


class MixerEntity(EconetEntity):
    """Represents MixerEntity."""

    def __init__(
        self,
        description: EntityDescription,
        coordinator: EconetDataCoordinator,
        api: Econet300Api,
        idx: int,
    ):
        super().__init__(description, coordinator, api)

        self._idx = idx

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device info of the entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._api.uid()}-mixer-{self._idx}")},
            name=DEVICE_INFO_MIXER_NAME,
            manufacturer=DEVICE_INFO_MANUFACTURER,
            model=DEVICE_INFO_MODEL,
            configuration_url=self._api.host(),
            sw_version=self._api.sw_rev(),
            via_device=(DOMAIN, self._api.uid()),
        )
