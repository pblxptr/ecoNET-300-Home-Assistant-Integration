import asyncio
import logging
import time
from datetime import timedelta
from http import HTTPStatus
from typing import Any

import async_timeout
from aiohttp import BasicAuth, ClientSession

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, API_SYS_PARAMS_URI, API_SYS_PARAMS_PARAM_UID, API_REG_PARAMS_URI, API_REG_PARAMS_PARAM_DATA, \
    API_EDITABLE_PARAMS_LIMITS_URI, API_EDITABLE_PARAMS_LIMITS_DATA, DEVICE_INFO_NAME, DEVICE_INFO_MANUFACTURER, \
    DEVICE_INFO_MODEL, EDITABLE_PARAMS_MAPPING_TABLE

from .mem_cache import MemCache

_LOGGER = logging.getLogger(__name__)


def map_param(param: str) -> Any | None:
    if param not in EDITABLE_PARAMS_MAPPING_TABLE:
        _LOGGER.debug("Mapping param: '{}' is 'None'".format(param))

        return None
    else:
        _LOGGER.debug("Mapping param: '{}' is '{}'".format(param, EDITABLE_PARAMS_MAPPING_TABLE[param]))

        return EDITABLE_PARAMS_MAPPING_TABLE[param]


class Limits:
    def __init__(self, min_v: float, max_v: float):
        self.min = min_v
        self.max = max_v

class AuthError(Exception):
    """AuthError"""


class ApiError(Exception):
    """AuthError"""


class DataError(Exception):
    """DataError"""


class EconetClient:
    def __init__(self, host: str, username: str, password: str, session: ClientSession) -> None:
        """Initialize."""

        if not "http://" in host or not "https://" in host:
            _LOGGER.warning("Manually adding 'http' to host")
            host = "http://" + host

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
                async with await self._get(self._host + "/econet/" + reg) as resp:

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
    def __init__(self, client: EconetClient, cache: MemCache) -> None:
        self._client = client
        self._cache = cache

    def host(self):
        return self._client.host()

    async def ping(self):
        await self.uid()

    async def uid(self) -> str:
        if not self._cache.exists(API_SYS_PARAMS_PARAM_UID):
            curr_uid = await self._fetch_reg_key(API_SYS_PARAMS_URI, API_SYS_PARAMS_PARAM_UID)
            self._cache.set(API_SYS_PARAMS_PARAM_UID, curr_uid)

        return self._cache.get(API_SYS_PARAMS_PARAM_UID)

    async def fetch_data(self):
        return await self._fetch_reg_key(API_REG_PARAMS_URI, API_REG_PARAMS_PARAM_DATA)

    async def get_param_limits(self, param: str):
        if not self._cache.exists(API_EDITABLE_PARAMS_LIMITS_DATA):
            limits = await self._fetch_editable_limits()
            self._cache.set(API_EDITABLE_PARAMS_LIMITS_DATA, limits)

        limits = self._cache.get(API_EDITABLE_PARAMS_LIMITS_DATA)

        print("Params limits: {}".format(limits))

        param_idx = map_param(param)

        if param_idx is None:
            _LOGGER.warning("Requested param limits for: '{}' but mapping for this param does not exist".format(param))
            return None

        if param_idx not in limits:
            _LOGGER.warning("Requested param limits for: '{}({})' but limits for this param do not exist".format(param, param_idx))
            return None

        curr_limits = limits[param_idx]
        return Limits(curr_limits["min"], curr_limits["max"])

    async def _fetch_editable_limits(self):
        return await self._fetch_reg_key(API_EDITABLE_PARAMS_LIMITS_URI, API_EDITABLE_PARAMS_LIMITS_DATA)

    async def _fetch_reg_key(self, reg_name, data_key):
        data = await self._client.get_params(reg_name)

        if data is None:
            raise DataError("Data fetched by API for reg: " + reg_name + " is None")

        if data_key not in data:
            _LOGGER.debug(data)
            raise DataError("Data for key: " + data_key + " does not exist")

        return data[data_key]


def make_api(hass: HomeAssistant, cache: MemCache, data: dict):
    return Econet300Api(
        EconetClient(
            data["host"],
            data["username"],
            data["password"],
            async_get_clientsession(hass)
        ), cache)


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
