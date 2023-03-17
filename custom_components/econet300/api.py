import asyncio
import logging
from http import HTTPStatus
from typing import Any

from aiohttp import ClientSession, BasicAuth
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_SYS_PARAMS_PARAM_UID, API_SYS_PARAMS_URI, API_REG_PARAMS_URI, API_REG_PARAMS_PARAM_DATA, \
    API_SYS_PARAMS_PARAM_SW_REV, API_EDITABLE_PARAMS_LIMITS_DATA, API_EDITABLE_PARAMS_LIMITS_URI, EDITABLE_PARAMS_MAPPING_TABLE
from .mem_cache import MemCache

_LOGGER = logging.getLogger(__name__)

def map_param(param_name):
    
    if not param_name in EDITABLE_PARAMS_MAPPING_TABLE:
        return None
    
    return EDITABLE_PARAMS_MAPPING_TABLE[param_name]


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

        proto = ["http://", "https://"]

        not_contains = all(p not in host for p in proto)

        if not_contains:
            _LOGGER.warning("Manually adding 'http' to host")
            host = "http://" + host

        self._host = host
        self._session = session
        self._auth = BasicAuth(username, password)

    def host(self):
        return self._host

    async def set_param(self, key: str, value: str):
        url = "{}/econet/rmCurrNewParam?newParamKey={}&newParamValue={}".format(
            self._host, key, value
        )

        return await self._get(url)

    async def get_params(self, reg: str):
        url = "{}/econet/{}".format(self._host, reg)

        return await self._get(url)

    async def _get(self, url):
        attempt = 0
        max_attempts = 5

        while ++attempt <= max_attempts:
            try:
                async with await self._session.get(url, auth=self._auth, timeout=10) as resp:

                    if resp.status == HTTPStatus.UNAUTHORIZED:
                        raise AuthError

                    elif resp.status != HTTPStatus.OK:
                        return None

                    return await resp.json()
            except TimeoutError as error:
                _LOGGER.warning("Timeout error, retry({}/{})".format(attempt, max_attempts))
                await asyncio.sleep(1)


class Econet300Api:
    def __init__(self, client: EconetClient, cache: MemCache) -> None:
        self._client = client
        self._cache = cache
        self._uid = "default-uid"
        self._sw_revision = "default-sw-revision"

    @classmethod
    async def create(cls, client: EconetClient, cache: MemCache):
        c = cls(client, cache)
        await c.init()

        return c

    def host(self):
        return self._client.host()

    def uid(self) -> str:
        return self._uid

    def sw_rev(self) -> str:
        return self._sw_revision

    async def init(self):
        sys_params = await self._client.get_params(API_SYS_PARAMS_URI)

        if API_SYS_PARAMS_PARAM_UID not in sys_params:
            _LOGGER.warning("{} not in sys_params - cannot set proper UUID".format(API_SYS_PARAMS_PARAM_UID))
        else:
            self._uid = sys_params[API_SYS_PARAMS_PARAM_UID]

        if API_SYS_PARAMS_PARAM_SW_REV not in sys_params:
            _LOGGER.warning("{} not in sys_params - cannot set proper sw_revision".format(API_SYS_PARAMS_PARAM_SW_REV))
        else:
            self._sw_revision = sys_params[API_SYS_PARAMS_PARAM_SW_REV]

    async def set_param(self, param, value) -> bool:
        param_idx = map_param(param)
        if param_idx is None:
            _LOGGER.warning("Requested param set for: '{}' but mapping for this param does not exist".format(param))
            return False

        data = await self._client.set_param(param_idx, value)

        if data is None or "result" not in data:
            return False

        if data["result"] != "OK":
            return False

        self._cache.set(param, value)
        
        return True

    async def fetch_data(self):
        return await self._fetch_reg_key(API_REG_PARAMS_URI, API_REG_PARAMS_PARAM_DATA)

    async def get_param_limits(self, param: str):
        if not self._cache.exists(API_EDITABLE_PARAMS_LIMITS_DATA):
            limits = await self._fetch_reg_key(API_EDITABLE_PARAMS_LIMITS_URI, API_EDITABLE_PARAMS_LIMITS_DATA)
            self._cache.set(API_EDITABLE_PARAMS_LIMITS_DATA, limits)

        limits = self._cache.get(API_EDITABLE_PARAMS_LIMITS_DATA)
        param_idx = map_param(param)

        if param_idx is None:
            _LOGGER.warning("Requested param limits for: '{}' but mapping for this param does not exist".format(param))
            return None

        if param_idx not in limits:
            _LOGGER.warning(
                "Requested param limits for: '{}({})' but limits for this param do not exist".format(param, param_idx))
            return None

        curr_limits = limits[param_idx]
        return Limits(curr_limits["min"], curr_limits["max"])


    async def _fetch_reg_key(self, reg, data_key):
        data = await self._client.get_params(reg)

        if data is None:
            raise DataError("Data fetched by API for reg: " + reg + " is None")

        if data_key not in data:
            _LOGGER.debug(data)
            raise DataError("Data for key: " + data_key + " does not exist")

        return data[data_key]


async def make_api(hass: HomeAssistant, cache: MemCache, data: dict):
    return await Econet300Api.create(
        EconetClient(
            data["host"],
            data["username"],
            data["password"],
            async_get_clientsession(hass)
        ), cache)
