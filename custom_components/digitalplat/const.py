"""Constantes de la integración DigitalPlat."""
from __future__ import annotations

DOMAIN = "digitalplat"
MANUFACTURER = "DigitalPlat"

API_BASE = "https://domain-api.digitalplat.org/api/v1"
DASHBOARD_URL = "https://dashboard.digitalplat.org/dashboard"
API_KEYS_URL = "https://dashboard.digitalplat.org/dashboard/api/keys"

# Datos de la entrada
CONF_API_KEY = "api_key"

# Opciones
CONF_DOMAINS = "domains"
CONF_WINDOW_DAYS = "window_days"
CONF_SCAN_HOURS = "scan_interval_hours"

# Panel de DigitalPlat: "La renovación gratuita está disponible dentro de los
# 120 días anteriores al vencimiento. Las renovaciones anticipadas usan créditos."
DEFAULT_WINDOW_DAYS = 120
DEFAULT_SCAN_HOURS = 6

# Estados en los que no tiene sentido ofrecer renovación.
BLOCKED_STATUSES = {"pendingdelete", "suspended", "disabled", "deleted", "locked"}
