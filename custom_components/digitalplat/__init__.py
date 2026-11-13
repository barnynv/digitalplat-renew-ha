"""Integración DigitalPlat Renew HA para Home Assistant."""
from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DigitalPlatApi
from .const import CONF_API_KEY, CONF_DOMAINS, DOMAIN
from .coordinator import DigitalPlatConfigEntry, DigitalPlatCoordinator

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.BUTTON]


async def async_setup_entry(hass: HomeAssistant, entry: DigitalPlatConfigEntry) -> bool:
    api = DigitalPlatApi(async_get_clientsession(hass), entry.data[CONF_API_KEY])
    coordinator = DigitalPlatCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    _remove_unselected_devices(hass, entry)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: DigitalPlatConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload(hass: HomeAssistant, entry: DigitalPlatConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


def _remove_unselected_devices(hass: HomeAssistant, entry: DigitalPlatConfigEntry) -> None:
    """Borra los dispositivos de dominios que el usuario ha desmarcado."""
    selected = set(entry.options.get(CONF_DOMAINS, []))
    registry = dr.async_get(hass)
    for device in dr.async_entries_for_config_entry(registry, entry.entry_id):
        names = {ident for (dom, ident) in device.identifiers if dom == DOMAIN}
        if names and not names & selected:
            registry.async_update_device(device.id, remove_config_entry_id=entry.entry_id)
