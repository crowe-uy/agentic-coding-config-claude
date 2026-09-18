# Configuración agéntica — Equipo de Automatizaciones

Este repositorio es la **fuente de cómo desarrollamos automatizaciones en Python** con asistencia de agentes de IA. Contiene dos cosas:

1. **Un plugin de Claude Code** (`plugins/automatizaciones/`) que cada desarrollador instala una vez. Aporta los agentes, los comandos del ciclo de implementación y los controles automáticos de calidad y seguridad.
2. **Una plantilla de proyecto** (`plugins/automatizaciones/plantilla-bot/`) que se copia cada vez que arranca una automatización nueva. Viaja dentro del plugin, así llega a todas las máquinas con la instalación.

## Instalación rápida

```bash
# Dentro de Claude Code, una sola vez por equipo:
/plugin marketplace add <organizacion>/agentic-coding-config-claude
/plugin install automatizaciones
```

El detalle está en [docs/instalacion.md](docs/instalacion.md).

## El ciclo en una línea

`/nuevo-bot` → `/relevamiento` → `/diseno` → **aprueba el referente** → `/implementar` → `/commit-pr` → `/manual-usuario` → `/release` → **validan desarrollador y referente** → producción.

El ciclo completo, con las aprobaciones y artefactos obligatorios de cada fase, está en [docs/ciclo-implementacion.md](docs/ciclo-implementacion.md).

## Comandos disponibles

| Comando | Fase | Qué hace |
|---|---|---|
| `/nuevo-bot` | Alta | Crea el proyecto desde la plantilla, con git, ramas y controles instalados |
| `/relevamiento` | 1 | Lee el relevamiento (Word/PDF) y produce el resumen sanitizado y las preguntas abiertas |
| `/diseno` | 1 | Diseña la solución y la documenta en un diagrama Mermaid con matriz de casos de uso |
| `/implementar` | 2 | Descompone el diseño aprobado en tareas y escribe código con sus pruebas |
| `/commit-pr` | 2 | Arma el commit y el PR con el detalle de funcionalidad y pruebas |
| `/manual-usuario` | 4 | Genera o actualiza el manual para el equipo de mantenimiento |
| `/release` | 3 | Crea la rama de release, ejecuta las pruebas y genera el informe `index.html` |
| `/bitacora` | Todas | Registra una entrada en la bitácora del ciclo |

## Documentación del equipo

- [Instalación y requisitos](docs/instalacion.md)
- [Ciclo de implementación](docs/ciclo-implementacion.md)
- [Convenciones de Git y GitHub](docs/convenciones-git.md)
- [Estándares de código Python](docs/estandares-python.md)
- [Seguridad y manejo de información sensible](docs/seguridad.md)

## Estructura

```
.claude-plugin/marketplace.json     Catálogo para instalar el plugin
plugins/automatizaciones/           El plugin: agentes, comandos, controles y scripts
  plantilla-bot/                    Esqueleto de una automatización nueva
docs/                               Documentación del equipo
pruebas/                            Pruebas de los scripts de este repositorio
```
