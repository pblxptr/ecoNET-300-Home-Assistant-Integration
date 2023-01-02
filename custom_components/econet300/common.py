import asyncio
import logging
from datetime import timedelta
from http import HTTPStatus
from typing import Any

import async_timeout
from aiohttp import BasicAuth, ClientSession

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, API_SYS_PARAMS, API_SYS_PARAMS_PARAM_UID, API_REG_PARAMS, API_REG_PARAMS_PARAM_DATA

_LOGGER = logging.getLogger(__name__)


class AuthError(Exception):
    """AuthError"""


class ApiError(Exception):
    """AuthError"""


class DataError(Exception):
    """DataError"""


class EconetClient:
    def __init__(self, host: str, username: str, password: str, session: ClientSession) -> None:
        """Initialize."""
        self._host = host
        self._session = session
        self._auth = BasicAuth(username, password)

    def host(self):
        return self._host

    async def get_params(self, reg):
        attempt = 0
        max_attempts = 5

        while ++attempt <= max_attempts:
            try:
                async with await self._get("http://" + self._host + "/econet/" + reg) as resp:

                    if resp.status == HTTPStatus.UNAUTHORIZED:
                        raise AuthError

                    elif resp.status != HTTPStatus.OK:
                        return None

                    return await resp.json()
            except TimeoutError as error:
                _LOGGER.warning("Timeout error, retry({}/{})".format(attempt, max_attempts))
                await asyncio.sleep(1)

    async def _get(self, url):
        return await self._session.get(url, auth=self._auth, timeout=10)


class Econet300Api:
    def __init__(self, client: EconetClient) -> None:
        self._client = client

    def host(self):
        return self._client.host()

    async def ping(self):
        await self.uid()

    async def uid(self) -> str:
        return await self._fetch_reg_key(API_SYS_PARAMS, API_SYS_PARAMS_PARAM_UID)

    async def fetch_data(self):
        return await self._fetch_reg_key(API_REG_PARAMS, API_REG_PARAMS_PARAM_DATA)

    async def _fetch_reg_key(self, reg_name, data_key):
        data = await self._client.get_params(reg_name)

        if data is None:
            raise DataError("Data fetched by API for reg: " + reg_name + " is None")

        if data_key not in data:
            _LOGGER.debug(data)
            raise DataError("Data for key: " + data_key + " does not exist")

        return data[data_key]


def make_api(hass: HomeAssistant, data: dict):
    return Econet300Api(EconetClient(
        data["host"],
        data["username"],
        data["password"],
        async_get_clientsession(hass)))


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
