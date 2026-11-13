"""Coordinador: una consulta a /domains por cuenta para todos sus dominios."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import DigitalPlatApi, DigitalPlatAuthError, DigitalPlatError, domain_name
from .const import (
    CONF_DOMAINS,
    CONF_SCAN_HOURS,
    CONF_WINDOW_DAYS,
    DEFAULT_SCAN_HOURS,
    DEFAULT_WINDOW_DAYS,
    DOMAIN,
)
from .models import DomainState, build_state

_LOGGER = logging.getLogger(__name__)

type DigitalPlatConfigEntry = ConfigEntry["DigitalPlatCoordinator"]


class DigitalPlatCoordinator(DataUpdateCoordinator[dict[str, DomainState]]):
    """Datos de todos los dominios seleccionados de una cuenta."""

    config_entry: DigitalPlatConfigEntry

    def __init__(self, hass: HomeAssistant, entry: DigitalPlatConfigEntry, api: DigitalPlatApi) -> None:
        hours = int(entry.options.get(CONF_SCAN_HOURS, DEFAULT_SCAN_HOURS))
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN} {entry.title}",
            update_interval=timedelta(hours=hours),
        )
        self.api = api

    @property
    def window_days(self) -> int:
        return int(self.config_entry.options.get(CONF_WINDOW_DAYS, DEFAULT_WINDOW_DAYS))

    @property
    def selected_domains(self) -> list[str]:
        return list(self.config_entry.options.get(CONF_DOMAINS, []))

    async def _async_update_data(self) -> dict[str, DomainState]:
        try:
            items = await self.api.list_domains()
        except DigitalPlatAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except DigitalPlatError as err:
            raise UpdateFailed(str(err)) from err

        by_name = {domain_name(i): i for i in items}
        today = dt_util.now().date()
        result: dict[str, DomainState] = {}
        for name in self.selected_domains:
            item = by_name.get(name)
            if item is None:
                _LOGGER.warning("El dominio %s ya no aparece en la cuenta de DigitalPlat", name)
                continue
            result[name] = build_state(name, item, today, self.window_days)
        return result
