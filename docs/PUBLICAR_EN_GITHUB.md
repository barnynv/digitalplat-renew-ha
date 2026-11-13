# Guía para publicar la integración en GitHub

Pasos para subir este repositorio a GitHub y que cualquiera pueda instalarlo con HACS.
No hace falta saber Git: el método A se hace todo desde el navegador.

---

## 0. Antes de subir: pon tus datos

Sustituye estos marcadores por los tuyos:

| Archivo | Buscar | Cambiar por |
|---|---|---|
| `custom_components/digitalplat/manifest.json` | `TU_USUARIO_GITHUB` (3 veces) | tu usuario de GitHub, sin `@` |
| `README.md` | `TU_USUARIO_GITHUB` (todas) | tu usuario de GitHub |
| `LICENSE` | `TU_NOMBRE` | tu nombre o alias |

En `manifest.json`, `codeowners` debe quedar con `@`, por ejemplo `["@miusuario"]`.

Con un editor como VS Code o Notepad++ puedes usar *Buscar y reemplazar en archivos*.

---

## 1. Crear el repositorio

1. Entra en <https://github.com/new>.
2. **Repository name:** `digitalplat-renew-ha`
3. **Description:** `Home Assistant integration to track and renew DigitalPlat free domains`
4. Marca **Public** (HACS necesita que sea público).
5. **No** marques "Add a README", ".gitignore" ni "license": ya vienen en el zip.
6. Pulsa **Create repository**.

---

## 2. Subir los archivos

### Método A: desde el navegador (sin instalar nada)
1. En la página del repositorio vacío, pulsa **uploading an existing file**.
2. Descomprime `digitalplat-renew-ha.zip` en tu ordenador y entra en la carpeta `digitalplat-renew-ha`.
3. Selecciona **todo su contenido** (no la carpeta en sí) y arrástralo a la web.
   - La carpeta `.github` está oculta en algunos sistemas. En Windows: Explorador → Vista → Mostrar → Elementos ocultos. En Mac: `Cmd + Shift + .`
   - Si la web no acepta `.github`, súbela después con el método B o créala a mano (*Add file → Create new file* y escribe `.github/workflows/validate.yml` como nombre).
4. Abajo, en *Commit changes*, escribe `Versión inicial 1.0.0` y pulsa **Commit changes**.

### Método B: con Git
```bash
cd digitalplat-renew-ha
git init
git add .
git commit -m "Versión inicial 1.0.0"
git branch -M main
git remote add origin https://github.com/TU_USUARIO_GITHUB/digitalplat-renew-ha.git
git push -u origin main
```

### Comprobación
En GitHub la raíz del repositorio debe verse así:
```
.github/
custom_components/
  └── digitalplat/
      ├── brand/          ← icono
      ├── translations/
      ├── manifest.json
      └── ...
docs/
examples/
CHANGELOG.md
CONTRIBUTING.md
hacs.json
LICENSE
README.md
```
Si ves una carpeta `digitalplat-renew-ha/` dentro del repositorio, has subido la carpeta en vez de su contenido: bórrala y repite.

---

## 3. Configurar el repositorio

En la página principal del repositorio, rueda dentada ⚙️ junto a **About**:
1. **Description:** la del paso 1.
2. **Topics:** `home-assistant`, `hacs`, `hacs-integration`, `digitalplat`, `homeassistant-integration`.
3. Guarda.

En **Settings → General → Features**, deja activado **Issues** para que te reporten errores.

---

## 4. Comprobar la validación automática

1. Pestaña **Actions**. Si pregunta, pulsa *I understand my workflows, go ahead and enable them*.
2. Abre **Validate → Run workflow** para lanzarlo a mano.
3. Los dos trabajos (**Hassfest** y **HACS**) deben salir en verde ✅.

Si alguno falla, abre el trabajo, copia el mensaje de error y corrígelo
(lo más habitual: un marcador `TU_USUARIO_GITHUB` sin cambiar o la descripción/topics vacíos).

---

## 5. Publicar la versión (release)

HACS instala a partir de las *releases*.

1. En el repositorio: **Releases → Create a new release** (o *Draft a new release*).
2. **Choose a tag:** escribe `v1.0.0` → *Create new tag*.
3. **Release title:** `v1.0.0`
4. En la descripción, copia la sección `1.0.0` del `CHANGELOG.md`.
5. Pulsa **Publish release**.

El número del tag debe coincidir con `version` de `manifest.json` (sin la `v`).

---

## 6. Instalarlo con HACS (tú y cualquier otro usuario)

1. En Home Assistant: **HACS → ⋮ → Repositorios personalizados**.
2. **Repositorio:** `https://github.com/TU_USUARIO_GITHUB/digitalplat-renew-ha`
3. **Tipo:** *Integración* → **Añadir**.
4. Busca **DigitalPlat Renew HA** en HACS → **Descargar** → reinicia Home Assistant.
5. **Ajustes → Dispositivos y servicios → Añadir integración → DigitalPlat Renew HA**.

> Si ya lo tenías copiado por Samba, borra antes `/config/custom_components/digitalplat`
> para que HACS lo gestione y te avise de las actualizaciones.

Puedes añadir este botón al README para que otros lo añadan con un clic
(ya está incluido, solo cambia el usuario):
```markdown
[![Abrir en HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=TU_USUARIO_GITHUB&repository=digitalplat-renew-ha&category=integration)
```

---

## 7. Publicar nuevas versiones

Cada vez que cambies algo:
1. Sube `version` en `manifest.json` (por ejemplo `1.0.1` para correcciones, `1.1.0` para funciones nuevas).
2. Añade la entrada en `CHANGELOG.md`.
3. Sube los cambios y crea una release con el tag `v1.0.1`.

Los usuarios verán la actualización en HACS y en **Ajustes → Actualizaciones**.

---

## 8. (Opcional) Aparecer en la tienda por defecto de HACS

Para que salga sin añadir repositorio personalizado, hay que pedir la inclusión en
[hacs/default](https://github.com/hacs/default). Requisitos principales:
- Validación de la Action en verde, al menos una release, descripción y topics.
- Seguir sus instrucciones de *pull request* en ese repositorio.

Consulta la guía oficial: <https://hacs.xyz/docs/publish/include>.

---

## Seguridad

- No subas nunca tu clave API, tu `secrets.yaml` ni capturas donde se vea.
- Si una clave se publica por error, revócala en DigitalPlat → API Keys y crea otra.
