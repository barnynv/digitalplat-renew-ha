"""Sensor binario por dominio: renovación gratuita disponible."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import DigitalPlatConfigEntry
from .entity import DigitalPlatEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: DigitalPlatConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(RenewalAvailable(coordinator, name) for name in coordinator.selected_domains)


class RenewalAvailable(DigitalPlatEntity, BinarySensorEntity):
    _attr_translation_key = "renewal_available"

    def __init__(self, coordinator, domain_name: str) -> None:
        super().__init__(coordinator, domain_name, "renewal_available")

    @property
    def is_on(self) -> bool | None:
        data = self.state_data
        return data.renewal_available if data else None
