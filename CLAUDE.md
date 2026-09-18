# Reglas de este repositorio

Este repo es la configuración agéntica del equipo de automatizaciones. No contiene automatizaciones: contiene **las reglas, los agentes y las herramientas** con las que se construyen.

## Idioma

Todo en español: documentación, prompts de agentes, mensajes de commit, nombres de funciones y variables.
**Excepción de forma:** los identificadores de código (módulos, funciones, variables, clases) van en español **sin tildes ni `ñ`** — `validar_parametrizacion`, `anio_proceso`, `ErrorNegocio`. Los textos visibles (docstrings, logs, mensajes de error, documentación) sí llevan tildes.

## Restricción crítica de los scripts y hooks del plugin

Los archivos bajo `plugins/automatizaciones/hooks/` y `plugins/automatizaciones/scripts/` se ejecutan con el **Python del sistema**, fuera del entorno virtual del bot.

- **Solo biblioteca estándar.** Nada de PyYAML, requests, jinja2 ni ninguna dependencia externa.
- Los catálogos de datos usan **TOML** (`tomllib`, estándar desde Python 3.11), no YAML.
- Los hooks nunca deben tardar más de un segundo ni escribir en el repositorio del usuario.
- Todo hook hace *no-op* si el proyecto no es un repo de automatización (no existe `docs/bitacora.md`): el plugin no debe estorbar en otros proyectos.

## Al modificar el plugin

- Si agregás o cambiás un comando, actualizá la tabla de `README.md` y `docs/ciclo-implementacion.md`.
- Si cambiás una plantilla de `plantilla-bot/docs/` (dentro del plugin), revisá que `scripts/verificar_ciclo.py` siga encontrando las secciones que valida.
- Las pruebas de los scripts viven en `pruebas/` y se corren con `python -m pytest pruebas/`.
- Validá la estructura del plugin con `claude plugin validate plugins/automatizaciones` antes de publicar.

## Sobre `plugins/automatizaciones/plantilla-bot/`

Es un esqueleto que se copia, no código que se ejecuta desde acá. Dos archivos llevan nombre alterado a propósito para que no afecten a este repositorio y `/nuevo-bot` los renombra al copiar:

- `gitignore.plantilla` → `.gitignore`
- `pre-commit.plantilla` → `.git/hooks/pre-commit`
