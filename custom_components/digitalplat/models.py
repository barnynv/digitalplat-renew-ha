"""Lógica pura (sin Home Assistant) para calcular el estado de cada dominio.

Separada del coordinador para poder probarla sin instalar Home Assistant.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any

from .const import BLOCKED_STATUSES


@dataclass
class DomainState:
    """Estado calculado de un dominio."""

    name: str
    status: str | None
    lifecycle_type: str | None
    expires: date | None
    window_opens: date | None
    days_left: int | None
    renewal_available: bool
    raw: dict[str, Any] = field(default_factory=dict)


def parse_date(value: Any) -> date | None:
    """Acepta '2027-11-06' o un datetime ISO 8601."""
    if not value:
        return None
    text = str(value).strip()
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        pass
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def build_state(name: str, item: dict[str, Any], today: date, window_days: int) -> DomainState:
    """Calcula caducidad, días restantes y si se puede renovar gratis hoy."""
    expires = parse_date(item.get("expires_at"))
    status = item.get("status")
    window_opens = expires - timedelta(days=window_days) if expires else None
    days_left = (expires - today).days if expires else None
    renewal_available = bool(
        window_opens is not None
        and today >= window_opens
        and str(status or "").lower() not in BLOCKED_STATUSES
    )
    return DomainState(
        name=name,
        status=status,
        lifecycle_type=item.get("lifecycle_type"),
        expires=expires,
        window_opens=window_opens,
        days_left=days_left,
        renewal_available=renewal_available,
        raw=item,
    )
