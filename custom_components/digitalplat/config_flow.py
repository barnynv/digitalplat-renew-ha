"""Formularios de configuración.

Alta:          1) clave API  →  2) elegir dominios de la cuenta
Opciones:      dominios vigilados, días del plazo de renovación, frecuencia
Reautenticar:  nueva clave cuando la actual deja de valer
Reconfigurar:  cambiar la clave de la misma cuenta sin borrar la integración
"""
from __future__ import annotations

import hashlib
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import (
    DigitalPlatApi,
    DigitalPlatAuthError,
    DigitalPlatConnectionError,
    DigitalPlatError,
    domain_name,
)
from .const import (
    API_KEYS_URL,
    CONF_API_KEY,
    CONF_DOMAINS,
    CONF_SCAN_HOURS,
    CONF_WINDOW_DAYS,
    DEFAULT_SCAN_HOURS,
    DEFAULT_WINDOW_DAYS,
    DOMAIN,
)

API_KEY_SELECTOR = TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD))


def _key_id(api_key: str) -> str:
    """Identificador estable de la cuenta sin guardar la clave en claro como id."""
    return hashlib.sha256(api_key.strip().encode()).hexdigest()[:16]


async def _fetch_domains(hass, api_key: str) -> tuple[list[dict[str, Any]], str | None]:
    """Devuelve (dominios, código_de_error)."""
    if not api_key.strip().startswith(("dp_live_", "dp_test_")):
        return [], "invalid_key_format"
    api = DigitalPlatApi(async_get_clientsession(hass), api_key)
    try:
        return await api.list_domains(), None
    except DigitalPlatAuthError:
        return [], "invalid_auth"
    except DigitalPlatConnectionError:
        return [], "cannot_connect"
    except DigitalPlatError:
        return [], "unknown"


def _domain_options(domains: list[dict[str, Any]]) -> list[SelectOptionDict]:
    options = []
    for item in domains:
        name = domain_name(item)
        expires = item.get("expires_at") or "—"
        options.append(SelectOptionDict(value=name, label=f"{name}  (expira: {expires})"))
    return sorted(options, key=lambda o: o["value"])


def _settings_schema(defaults: dict[str, Any]) -> dict:
    return {
        vol.Required(
            CONF_WINDOW_DAYS, default=defaults.get(CONF_WINDOW_DAYS, DEFAULT_WINDOW_DAYS)
        ): NumberSelector(
            NumberSelectorConfig(min=1, max=365, step=1, mode=NumberSelectorMode.BOX, unit_of_measurement="d")
        ),
        vol.Required(
            CONF_SCAN_HOURS, default=defaults.get(CONF_SCAN_HOURS, DEFAULT_SCAN_HOURS)
        ): NumberSelector(
            NumberSelectorConfig(min=1, max=48, step=1, mode=NumberSelectorMode.BOX, unit_of_measurement="h")
        ),
    }


def _normalize(user_input: dict[str, Any]) -> dict[str, Any]:
    return {
        CONF_DOMAINS: list(user_input[CONF_DOMAINS]),
        CONF_WINDOW_DAYS: int(user_input[CONF_WINDOW_DAYS]),
        CONF_SCAN_HOURS: int(user_input[CONF_SCAN_HOURS]),
    }


class DigitalPlatConfigFlow(ConfigFlow, domain=DOMAIN):
    """Alta de una cuenta de DigitalPlat."""

    VERSION = 1

    def __init__(self) -> None:
        self._api_key: str = ""
        self._domains: list[dict[str, Any]] = []

    # ── Paso 1: clave API ─────────────────────────────────────────────
    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            domains, error = await _fetch_domains(self.hass, api_key)
            if error:
                errors["base"] = error
            elif not domains:
                errors["base"] = "no_domains"
            else:
                await self.async_set_unique_id(_key_id(api_key))
                self._abort_if_unique_id_configured()
                self._api_key = api_key
                self._domains = domains
                return await self.async_step_domains()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): API_KEY_SELECTOR}),
            errors=errors,
            description_placeholders={"api_keys_url": API_KEYS_URL},
        )

    # ── Paso 2: dominios y ajustes ────────────────────────────────────
    async def async_step_domains(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            if not user_input.get(CONF_DOMAINS):
                errors["base"] = "select_domain"
            else:
                options = _normalize(user_input)
                title = options[CONF_DOMAINS][0] if len(options[CONF_DOMAINS]) == 1 else (
                    f"DigitalPlat ({len(options[CONF_DOMAINS])} dominios)"
                )
                return self.async_create_entry(
                    title=title, data={CONF_API_KEY: self._api_key}, options=options
                )

        all_names = [domain_name(d) for d in self._domains]
        schema = vol.Schema(
            {
                vol.Required(CONF_DOMAINS, default=all_names): SelectSelector(
                    SelectSelectorConfig(
                        options=_domain_options(self._domains),
                        multiple=True,
                        mode=SelectSelectorMode.LIST,
                    )
                ),
                **_settings_schema({}),
            }
        )
        return self.async_show_form(step_id="domains", data_schema=schema, errors=errors)

    # ── Reautenticación ───────────────────────────────────────────────
    async def async_step_reauth(self, entry_data: dict[str, Any]) -> ConfigFlowResult:
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return await self._async_new_key_step("reauth_confirm", self._get_reauth_entry(), user_input)

    # ── Reconfigurar (cambiar clave) ──────────────────────────────────
    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return await self._async_new_key_step("reconfigure", self._get_reconfigure_entry(), user_input)

    async def _async_new_key_step(
        self, step_id: str, entry: ConfigEntry, user_input: dict[str, Any] | None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            domains, error = await _fetch_domains(self.hass, api_key)
            names = {domain_name(d) for d in domains}
            if error:
                errors["base"] = error
            elif not names & set(entry.options.get(CONF_DOMAINS, [])):
                # La clave debe ser de la misma cuenta que los dominios vigilados.
                errors["base"] = "wrong_account"
            else:
                return self.async_update_reload_and_abort(
                    entry, unique_id=_key_id(api_key), data_updates={CONF_API_KEY: api_key}
                )
        return self.async_show_form(
            step_id=step_id,
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): API_KEY_SELECTOR}),
            errors=errors,
            description_placeholders={"api_keys_url": API_KEYS_URL},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return DigitalPlatOptionsFlow()


class DigitalPlatOptionsFlow(OptionsFlow):
    """Cambiar dominios vigilados y ajustes sin volver a dar de alta la cuenta."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            if not user_input.get(CONF_DOMAINS):
                errors["base"] = "select_domain"
            else:
                return self.async_create_entry(data=_normalize(user_input))

        current = dict(self.config_entry.options)
        domains, error = await _fetch_domains(self.hass, self.config_entry.data[CONF_API_KEY])
        if error:
            errors["base"] = error
        options = _domain_options(domains)
        known = {o["value"] for o in options}
        # Conserva los dominios ya elegidos aunque la API no responda ahora.
        for name in current.get(CONF_DOMAINS, []):
            if name not in known:
                options.append(SelectOptionDict(value=name, label=name))

        schema = vol.Schema(
            {
                vol.Required(CONF_DOMAINS, default=current.get(CONF_DOMAINS, [])): SelectSelector(
                    SelectSelectorConfig(options=options, multiple=True, mode=SelectSelectorMode.LIST)
                ),
                **_settings_schema(current),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
