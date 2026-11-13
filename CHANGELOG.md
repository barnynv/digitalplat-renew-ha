# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y versionado [SemVer](https://semver.org/lang/es/).

## [1.0.0] - 2026-11-13
Primera versión pública.

### Funciones
- Configuración desde la interfaz: clave API de DigitalPlat y selección de los dominios de la cuenta.
- Varios dominios por cuenta y varias cuentas por instalación.
- Por cada dominio: fecha de expiración, días restantes, apertura de la renovación gratuita,
  estado y sensor "Renovación disponible".
- Botón **Renovar** que solo se habilita dentro del plazo de renovación gratuita
  (120 días por defecto, configurable). Envía una única petición con `Idempotency-Key`
  y notifica el resultado.
- Opciones para cambiar dominios, plazo y frecuencia de consulta.
- Reautenticación automática y opción **Reconfigurar** para cambiar la clave.
- Diagnóstico descargable con la clave oculta.
- Interfaz en español e inglés, iconos de entidades e icono propio de la integración (HA 2026.3+).
- Compatible con HACS; validación con hassfest y HACS en GitHub Actions.
