"""Entidad base: un dispositivo por dominio."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DASHBOARD_URL, DOMAIN, MANUFACTURER
from .coordinator import DigitalPlatCoordinator
from .models import DomainState


class DigitalPlatEntity(CoordinatorEntity[DigitalPlatCoordinator]):
    """Entidad ligada a un dominio concreto."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: DigitalPlatCoordinator, domain_name: str, key: str) -> None:
        super().__init__(coordinator)
        self.domain_name = domain_name
        self._attr_unique_id = f"{domain_name}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, domain_name)},
            name=domain_name,
            manufacturer=MANUFACTURER,
            model="Domain",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=DASHBOARD_URL,
        )

    @property
    def state_data(self) -> DomainState | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self.domain_name)

    @property
    def available(self) -> bool:
        return super().available and self.state_data is not None
