"""Botón "Renovar" por dominio, gemelo del de la web de DigitalPlat.

Solo está disponible dentro del plazo de renovación gratuita. Fuera de él
aparece como no disponible y no se puede pulsar, para no gastar créditos en
una renovación anticipada.
"""
from __future__ import annotations

import logging

from homeassistant.components import persistent_notification
from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import DigitalPlatError
from .const import DOMAIN
from .coordinator import DigitalPlatConfigEntry
from .entity import DigitalPlatEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: DigitalPlatConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(RenewButton(coordinator, name) for name in coordinator.selected_domains)


class RenewButton(DigitalPlatEntity, ButtonEntity):
    _attr_translation_key = "renew"

    def __init__(self, coordinator, domain_name: str) -> None:
        super().__init__(coordinator, domain_name, "renew")

    @property
    def available(self) -> bool:
        data = self.state_data
        return super().available and data is not None and data.renewal_available

    async def async_press(self) -> None:
        coord = self.coordinator
        name = self.domain_name

        # Datos frescos antes de actuar.
        await coord.async_refresh()
        data = self.state_data
        if data is None or not data.renewal_available:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="renewal_not_available",
                translation_placeholders={"domain": name},
            )

        before = data.expires
        try:
            await coord.api.renew(name)
        except DigitalPlatError as err:
            # Nunca se reintenta automáticamente una renovación.
            await coord.async_refresh()
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="renewal_failed",
                translation_placeholders={"domain": name, "error": str(err)},
            ) from err

        await coord.async_refresh()
        after = self.state_data.expires if self.state_data else None

        if after and before and after > before:
            message = f"✅ {name} renovado. Nueva fecha de expiración: {after.isoformat()}."
        else:
            message = (
                f"Se envió la renovación de {name}, pero la fecha de expiración sigue "
                f"siendo {after}. Revisa el panel de DigitalPlat antes de repetir."
            )
        _LOGGER.info(message)
        persistent_notification.async_create(
            self.hass, message, title="DigitalPlat", notification_id=f"{DOMAIN}_{name}_renew"
        )
