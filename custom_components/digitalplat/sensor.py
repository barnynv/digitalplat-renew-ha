"""Sensores por dominio: caducidad, días restantes y apertura de la renovación."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import DigitalPlatConfigEntry
from .entity import DigitalPlatEntity
from .models import DomainState


@dataclass(frozen=True, kw_only=True)
class DPSensorDescription(SensorEntityDescription):
    value_fn: Callable[[DomainState], Any]


SENSORS: tuple[DPSensorDescription, ...] = (
    DPSensorDescription(
        key="expires",
        translation_key="expires",
        device_class=SensorDeviceClass.DATE,
        value_fn=lambda d: d.expires,
    ),
    DPSensorDescription(
        key="days_left",
        translation_key="days_left",
        native_unit_of_measurement=UnitOfTime.DAYS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.days_left,
    ),
    DPSensorDescription(
        key="window_opens",
        translation_key="window_opens",
        device_class=SensorDeviceClass.DATE,
        value_fn=lambda d: d.window_opens,
    ),
    DPSensorDescription(
        key="status",
        translation_key="status",
        value_fn=lambda d: d.status,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: DigitalPlatConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        DigitalPlatSensor(coordinator, name, desc)
        for name in coordinator.selected_domains
        for desc in SENSORS
    )


class DigitalPlatSensor(DigitalPlatEntity, SensorEntity):
    entity_description: DPSensorDescription

    def __init__(self, coordinator, domain_name: str, description: DPSensorDescription) -> None:
        super().__init__(coordinator, domain_name, description.key)
        self.entity_description = description

    @property
    def native_value(self):
        data = self.state_data
        return self.entity_description.value_fn(data) if data else None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        data = self.state_data
        if data is None or self.entity_description.key != "expires":
            return None
        return {
            "lifecycle_type": data.lifecycle_type,
            "slot_type": data.raw.get("slot_type"),
            "nameservers": data.raw.get("nameservers"),
            "renewal_window_days": self.coordinator.window_days,
        }
