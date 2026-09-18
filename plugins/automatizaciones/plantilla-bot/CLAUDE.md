# <NOMBRE_DEL_BOT>

Automatización en Python del equipo de automatizaciones. Este archivo define cómo se trabaja en este proyecto; el detalle completo está en el plugin `automatizaciones`.

## Reglas que no se negocian

1. **Ningún cambio de código sin su prueba.** Si cambia el comportamiento, cambian las pruebas.
2. **Nada sensible al repositorio**: ni el relevamiento, ni credenciales, ni datos reales. Ver `docs/seguridad` del plugin.
3. **No se commitea ni se pushea directo a `main` ni a `dev`.** Todo entra por PR.
4. **La bitácora se actualiza en cada hito**: decisión tomada, PR abierto, prueba ejecutada.
5. **No se escribe código productivo sin el diseño aprobado** por el referente técnico.

## Idioma

Todo en español. Identificadores de código **sin tildes ni `ñ`** (`validar_periodo`, `anio`, `ErrorNegocio`); docstrings, logs y documentación con tildes.

## Estructura

```
src/paquete_bot/     Código: principal, configuracion, registro, errores, reintentos, conectores/
pruebas/             unitarias/ (lógica pura) · integracion/ (conectores con dobles) · e2e/ (marcadas)
docs/                bitacora · diseno/solucion · manual-usuario · accesos · pruebas/casos.toml
datos/ejemplo/       Parametrizaciones de ejemplo, con datos ficticios
relevamiento/        IGNORADA POR GIT. El documento original vive acá y no se sube nunca
```

## Cómo se escribe el código acá

- Toda excepción propia hereda de **`ErrorNegocio`** (dato o situación inválida, **no se reintenta**) o **`ErrorSistema`** (falla técnica transitoria, **se reintenta**). Clasificar mal esto es la causa principal de bots frágiles.
- Cada sistema externo va detrás de un **conector** en `conectores/`. `principal.py` nunca llama directo a Playwright, pywinauto ni `requests`.
- **Nunca `time.sleep()` para esperar algo**: se espera por la condición con `esperar_hasta(...)`.
- **Nunca `except:` desnudo ni `except Exception: pass`**. Si se ignora una excepción, se comenta por qué.
- Las credenciales se leen de `.env` con `obtener_variable(...)`; toda variable nueva se agrega a `.env.example`.
- Tipado en las firmas públicas, docstrings en español, `pathlib.Path` para rutas.
- `principal.py` debe leerse como el diagrama de `docs/diseno/solucion.md`. Si no se parecen, uno de los dos está desactualizado.

## Comandos

```bash
python -m venv .venv && .venv\Scripts\activate    # Windows
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest                                   # todas menos e2e
python -m pytest -m e2e                            # solo e2e (requiere entorno real)
ruff format . && ruff check --fix .
python ejecutar.py                                 # ejecutar el bot
```

## Comandos del ciclo

`/relevamiento` · `/diseno` · `/implementar` · `/commit-pr` · `/manual-usuario` · `/release` · `/bitacora`
