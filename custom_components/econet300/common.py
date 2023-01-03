import logging
from datetime import timedelta
from typing import Any

import async_timeout
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import Econet300Api, AuthError, ApiError
from .const import EDITABLE_PARAMS_MAPPING_TABLE, DOMAIN

_LOGGER = logging.getLogger(__name__)


class EconetDataCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass, api: Econet300Api):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=30),
        )
        self._api = api

    def has_data(self, key: str):
        return key in self.data

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """

        _LOGGER.debug("Fetching data from API")

        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(10):
                return await self._api.fetch_data()
        except AuthError as err:
            raise ConfigEntryAuthFailed from err
        except ApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
