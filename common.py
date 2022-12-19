import logging
from datetime import timedelta
from http import HTTPStatus

import async_timeout
from aiohttp import BasicAuth, ClientSession

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class AuthError(Exception):
    """AuthError"""


class ApiError(Exception):
    """AuthError"""


class EconetClient:
    def __init__(self, host: str, username: str, password: str, session: ClientSession) -> None:
        """Initialize."""
        self._host = host
        self._session = session
        self._auth = BasicAuth(username, password)

    def host(self):
        return self._host

    async def get_reg_params(self):
        return await self.get_params("regParams")

    async def get_sys_params(self):
        return await self.get_params("sysParams")

    async def get_params(self, reg):
        async with await self._get("http://" + self._host + "/econet/" + reg) as resp:

            if resp.status == HTTPStatus.UNAUTHORIZED:
                raise AuthError

            elif resp.status != HTTPStatus.OK:
                return None

            return await resp.json()

    async def _get(self, url):
        return await self._session.get(url, auth=self._auth, timeout=5)


class Econet300Api:
    def __init__(self, client: EconetClient) -> None:
        self._client = client

    def host(self):
        return self._client.host()

    async def ping(self):
        await self._client.get_sys_params()

    async def uid(self) -> str:
        data = await self._client.get_sys_params()

        return data["uid"]

    async def fetch_data(self):
        data = await self._client.get_reg_params()

        return data["curr"]

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

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(10):
                return await self._api.fetch_data()
        except AuthError as err:
            raise ConfigEntryAuthFailed from err
        except ApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
