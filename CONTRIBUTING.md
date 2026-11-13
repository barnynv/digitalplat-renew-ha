# Cómo contribuir

¡Gracias por ayudar! Issues y pull requests son bienvenidos.

## Reportar un problema
1. Activa el registro detallado en `configuration.yaml` y reinicia:
   ```yaml
   logger:
     default: warning
     logs:
       custom_components.digitalplat: debug
   ```
2. Reproduce el problema y copia las líneas de **Ajustes → Sistema → Registros** que contengan `digitalplat`.
3. Si puedes, descarga el diagnóstico: **Ajustes → Dispositivos y servicios → DigitalPlat Renew HA → ⋮ → Descargar diagnóstico**. La clave API sale oculta.
4. Abre un issue con la plantilla *Error*.

**Nunca pegues tu clave API** (`dp_live_...`) en un issue. Si lo haces por error, revócala en DigitalPlat.

## Estructura del código

| Archivo | Función |
|---|---|
| `api.py` | Cliente HTTP de la API de DigitalPlat (`/domains`, `/domains/{d}/renew`) |
| `models.py` | Cálculo de caducidad y plazo de renovación (sin dependencias de HA, fácil de probar) |
| `coordinator.py` | Consulta periódica de todos los dominios de una cuenta |
| `config_flow.py` | Formularios: alta, opciones, reautenticación y reconfiguración |
| `sensor.py`, `binary_sensor.py`, `button.py` | Entidades por dominio |
| `diagnostics.py` | Diagnóstico descargable |
| `strings.json`, `translations/` | Textos de la interfaz (inglés y español) |
| `icons.json` | Iconos de las entidades |
| `brand/` | Icono de la integración (HA 2026.3+) |

## Desarrollo
1. Haz un fork y crea una rama: `git checkout -b mi-mejora`.
2. Prueba en una instalación de Home Assistant de pruebas copiando `custom_components/digitalplat` a `/config/custom_components/` y reiniciando.
3. Si cambias textos, actualiza **los tres** archivos: `strings.json`, `translations/en.json` y `translations/es.json`, con las mismas claves.
4. Comprueba que el código compila: `python -m py_compile custom_components/digitalplat/*.py`.
5. Abre el pull request. La GitHub Action ejecuta *hassfest* y la validación de HACS.

## Publicar una versión (mantenedores)
1. Sube `version` en `manifest.json` (SemVer).
2. Añade la entrada en `CHANGELOG.md`.
3. Commit, tag y release en GitHub con el mismo número: `v1.0.0`.
HACS ofrece la actualización a los usuarios a partir de la release.
