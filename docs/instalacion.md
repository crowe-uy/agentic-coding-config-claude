# Instalación y requisitos

## Requisitos en el equipo del desarrollador

| Requisito | Versión | Cómo verificar |
|---|---|---|
| Python | 3.14 | `python --version` |
| Git | 2.40+ | `git --version` |
| GitHub CLI | 2.40+ | `gh --version` |
| Claude Code | Última | `claude --version` |

Python debe estar **en el PATH** con el nombre `python`: los controles automáticos del plugin se ejecutan con ese comando.

### Autenticar GitHub CLI

```bash
gh auth login
```

Si el comando queda esperando una respuesta interactiva, ejecutalo desde la terminal con `! gh auth login` dentro de Claude Code.

## Instalar el plugin

Una sola vez por equipo:

```
/plugin marketplace add <organizacion>/agentic-coding-config-claude
/plugin install automatizaciones
```

Para probar cambios locales del plugin sin publicar:

```
/plugin marketplace add C:/Users/<usuario>/Desktop/agentic-coding-config-claude
/plugin install automatizaciones
```

Verificar que quedó activo:

```
/plugin
```

Deben aparecer los ocho comandos (`/nuevo-bot`, `/relevamiento`, `/diseno`, `/implementar`, `/commit-pr`, `/manual-usuario`, `/release`, `/bitacora`) y los seis agentes.

## Actualizar el plugin

```
/plugin marketplace update automatizaciones-marketplace
```

Los cambios del ciclo, los estándares y los controles llegan a todos los desarrolladores desde acá. Las automatizaciones ya creadas **no** se actualizan solas: su `plantilla-bot` fue copiada en el momento del alta. Si un cambio en la plantilla es importante para bots existentes, se comunica al equipo y se aplica con un `fix/*`.

## Crear la primera automatización

```
/nuevo-bot facturacion-proveedores
```

El comando pide la ruta destino, crea el proyecto, inicializa git con `main` y `dev`, e instala el control previo al commit.

## Problemas frecuentes

**"Los controles no se ejecutan."** El plugin hace *no-op* fuera de un repo de automatización: verificá que exista `docs/bitacora.md` en la raíz del proyecto.

**"`python` no se encuentra" al editar un archivo.** Python no está en el PATH del sistema (tenerlo dentro del `.venv` no alcanza). Reinstalá Python marcando "Add to PATH".

**"El comando `/relevamiento` no encuentra el documento."** El documento debe estar en la carpeta `relevamiento/` del proyecto, en `.docx` o `.pdf`. Esa carpeta está ignorada por git a propósito.
