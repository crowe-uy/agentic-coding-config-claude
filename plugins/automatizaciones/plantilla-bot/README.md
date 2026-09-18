# <NOMBRE_DEL_BOT>

<Una línea: qué automatiza este bot y para quién.>

| | |
|---|---|
| **Versión en producción** | — |
| **Estado** | En desarrollo |
| **Desarrollador** | |
| **Referente técnico** | |

## Documentación

| Documento | Para qué |
|---|---|
| [Manual de usuario](docs/manual-usuario.md) | Operar y mantener el bot |
| [Diseño de la solución](docs/diseno/solucion.md) | Entender el flujo |
| [Bitácora](docs/bitacora.md) | Historia del ciclo de implementación |
| [Resumen del relevamiento](docs/relevamiento-resumen.md) | Qué pidió el negocio |
| [Catálogo de pruebas](docs/pruebas/casos.toml) | Qué se prueba y cómo |

## Puesta en marcha

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
copy .env.example .env.local   # tus credenciales, solo en tu máquina
python -m pytest            # verificar que todo pasa
python ejecutar.py          # ejecutar el bot
```

## Estructura

```
src/paquete_bot/     Código de la automatización
pruebas/             unitarias · integracion · e2e
docs/                Documentación del ciclo
parametros/ejemplo/  Parametrizaciones de ejemplo (datos ficticios; la real suele vivir afuera, ver .env.example)
recursos/            Plantillas y archivos de referencia que el bot usa pero el usuario no edita
relevamiento/        Documento original — IGNORADO POR GIT
```

## Ramas

`main` es productiva · `dev` integra el desarrollo · `feature/*` y `fix/*` entran a `dev` · `release/X.Y.Z` y `hotfix/*` entran a `main`.

Nada se commitea directo a `main` ni a `dev`.
