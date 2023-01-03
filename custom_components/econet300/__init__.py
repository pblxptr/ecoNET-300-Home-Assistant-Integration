"""The Example Integration integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, ConfigEntryAuthFailed
from .common import make_api, AuthError, EconetDataCoordinator
from .const import DOMAIN, SERVICE_API, SERVICE_COORDINATOR

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.NUMBER]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Econet300 Integration from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    api = make_api(hass, entry.data)

    try:
        await api.ping()
    except AuthError as auth_error:
        raise ConfigEntryAuthFailed("Client not authenticated")
    except TimeoutError as timeout_error:
        raise ConfigEntryNotReady("Target not found")

    coordinator = EconetDataCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        SERVICE_API: api,
        SERVICE_COORDINATOR: coordinator
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
