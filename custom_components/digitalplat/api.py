"""Cliente asíncrono para la API pública de DigitalPlat.

Documentación oficial (requiere sesión):
https://dashboard.digitalplat.org/dashboard/api/docs
"""
from __future__ import annotations

from typing import Any
import uuid

import aiohttp

from .const import API_BASE

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=30)


class DigitalPlatError(Exception):
    """Error genérico de la API."""


class DigitalPlatConnectionError(DigitalPlatError):
    """No se pudo contactar con DigitalPlat."""


class DigitalPlatAuthError(DigitalPlatError):
    """Clave API no válida, revocada o sin permisos."""


class DigitalPlatApi:
    """Llamadas a la API v1 de DigitalPlat."""

    def __init__(self, session: aiohttp.ClientSession, api_key: str) -> None:
        self._session = session
        self._api_key = api_key.strip()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        extra_headers: dict[str, str] | None = None,
        json: Any = None,
    ) -> Any:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
            "User-Agent": "HomeAssistant-DigitalPlat",
        }
        if extra_headers:
            headers.update(extra_headers)
        try:
            async with self._session.request(
                method, f"{API_BASE}{path}", headers=headers, json=json, timeout=REQUEST_TIMEOUT
            ) as resp:
                try:
                    payload = await resp.json(content_type=None)
                except ValueError:
                    payload = None
                status = resp.status
        except (aiohttp.ClientError, TimeoutError) as err:
            raise DigitalPlatConnectionError(f"No se pudo conectar con DigitalPlat: {err}") from err

        if status in (401, 403):
            raise DigitalPlatAuthError(error_text(payload, status))
        if status >= 400:
            raise DigitalPlatError(error_text(payload, status))
        if not isinstance(payload, dict) or payload.get("success") is not True:
            raise DigitalPlatError(error_text(payload, status))
        return payload.get("data")

    async def list_domains(self) -> list[dict[str, Any]]:
        """GET /domains: todos los dominios de la cuenta de la clave."""
        data = await self._request("GET", "/domains")
        if not isinstance(data, list):
            return []
        return [d for d in data if isinstance(d, dict) and domain_name(d)]

    async def renew(self, name: str) -> Any:
        """POST /domains/{dominio}/renew.

        La Idempotency-Key evita que una petición duplicada por la red se
        procese dos veces.
        """
        return await self._request(
            "POST",
            f"/domains/{name}/renew",
            extra_headers={"Content-Type": "application/json", "Idempotency-Key": str(uuid.uuid4())},
            json={},
        )


def domain_name(item: dict[str, Any]) -> str:
    """El listado usa 'domain'; otras respuestas usan 'name'."""
    return str(item.get("domain") or item.get("name") or "").strip().lower()


def error_text(payload: Any, status: int) -> str:
    """Extrae un mensaje legible de una respuesta de error."""
    if isinstance(payload, dict):
        err = payload.get("error") or payload.get("message")
        if isinstance(err, dict):
            err = err.get("message") or err.get("code")
        if err:
            return f"{err} (HTTP {status})"
    return f"Respuesta inesperada de DigitalPlat (HTTP {status})"
