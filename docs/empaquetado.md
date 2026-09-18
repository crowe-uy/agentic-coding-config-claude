# Empaquetado en .exe

Algunos clientes no permiten instalar Python en sus equipos. Para esos casos, el bot se empaqueta con **PyInstaller** en un `.exe` standalone: el cliente lo recibe y lo ejecuta sin instalar nada.

Es opcional: si el bot corre en un equipo del cliente (o propio) donde sí se puede instalar Python, no hace falta empaquetarlo — `python ejecutar.py` alcanza.

## Cómo funciona en este repo

Cada bot trae `paquete.spec` en su raíz, listo para usar:

```bash
pip install -r requirements.txt -r requirements-dev.txt   # incluye pyinstaller
pyinstaller paquete.spec
```

Genera `dist/<paquete>.exe`. `build/` y `dist/` están en `.gitignore`: son salidas, no se versionan — el `.spec` sí, porque es configuración reproducible.

## Por qué hubo que tocar el código para esto

Un `.exe` lanzado por el Programador de tareas de Windows **no garantiza el directorio de trabajo**. Antes de esto, `logs/`, `salida/` y la búsqueda de `.env*` eran rutas relativas al directorio de trabajo — funcionaba corriendo `python ejecutar.py` desde la carpeta del proyecto, pero un `.exe` programado podía terminar buscando el `.env` o escribiendo logs en cualquier lado, según cómo lo lanzara la tarea.

`src/paquete_bot/entorno.py` resuelve esto con `raiz_ejecucion()`: empaquetado, la base es la carpeta donde está el `.exe` (`Path(sys.executable).parent`); desde código fuente, el directorio de trabajo actual, como siempre. `configuracion.py` y `registro.py` anclan ahí la búsqueda de `.env*`, `logs/` y `salida/` por defecto.

**Esto significa que el `.exe` y el `.env` (o `.env.local`) tienen que estar en la misma carpeta.** Es la forma más simple de garantizar que el bot encuentre sus credenciales sin importar quién lo lance.

## Onefile vs. onedir

`paquete.spec` genera **onefile** (un solo `.exe`) por defecto: lo más simple para entregarle al cliente un solo archivo. Contras conocidos:

- Arranca un poco más lento (se descomprime a una carpeta temporal en cada corrida).
- Algunos antivirus corporativos lo marcan como sospechoso por cómo empaqueta el binario — es un falso positivo conocido de PyInstaller, no del código del bot, pero puede requerir que el cliente lo agregue a una lista blanca.

Si eso da problemas, **onedir** (una carpeta con el `.exe` y sus dependencias sueltas) arranca más rápido y genera menos falsos positivos, a cambio de entregar una carpeta en vez de un archivo. El cambio está comentado, listo para descomentar, en el propio `paquete.spec`.

## Limitación importante: Playwright

Si el bot usa `ConectorWeb` (Playwright), el `.exe` **no incluye los binarios del navegador** — son un descargable aparte (`playwright install chromium`), no parte del paquete de Python, y PyInstaller no los empaqueta solo. El equipo destino necesita:

- Chromium instalado vía `playwright install chromium` (requiere tener Python ahí, aunque sea momentáneamente, para ese único paso), o
- Apuntar el conector a un navegador ya instalado en el equipo (`channel="chrome"` en vez de lanzar el Chromium de Playwright).

Para pywinauto (escritorio) y SAP GUI Scripting no hay problema extra: dependen de que la aplicación de escritorio o SAP GUI ya estén instalados en el equipo, que es un requisito del bot de todos modos, empaquetado o no — documentalo en las precondiciones del manual de usuario.

## Versión del .exe

Nombrá el archivo entregado con la versión del release, para que quede trazable: `<paquete>-X.Y.Z.exe`. Como `__version__` en `src/<paquete>/__init__.py` ya queda sincronizado con cada release (ver [convenciones-git.md](convenciones-git.md)), y el bot lo loguea al arrancar, un log de producción siempre dice con qué build corrió.

## Entrega al cliente

No hay un mecanismo automático de distribución. Dos opciones razonables:

1. **Adjuntarlo al release de GitHub**, sobre el tag que ya crea `/release`: `gh release create vX.Y.Z dist/<paquete>-X.Y.Z.exe --title "vX.Y.Z" --notes "..."`. Queda versionado y trazable al commit exacto.
2. **Copiarlo directo** al equipo del cliente (pendrive, carpeta compartida, lo que use el proyecto), junto con `.env` completado y la carpeta `datos/` si el bot tiene parametrizaciones.

En cualquiera de los dos casos, documentá en `docs/manual-usuario.md` cómo el equipo de mantenimiento reconstruye el `.exe` si hace falta un cambio — ver la sección "Cómo ejecutar la automatización" del manual.

## Verificar antes de entregar

Corré el `.exe` generado desde una carpeta distinta a la del build (para confirmar que `raiz_ejecucion()` realmente ancla bien las rutas) y revisá:

- Que `logs/` y `salida/` aparezcan junto al `.exe`, no donde lo lanzaste.
- Que sin `.env` (ni `.env.local` ni `.env.dev`) el bot falle con `ErrorConfiguracion`, no con un traceback de Python sin manejar.
- El código de salida (`0`, `1` o `2` — ver `docs/manual-usuario.md` del bot).

> Nota menor: en algunas consolas de Windows los acentos se ven mal en pantalla (`versi�n` en vez de `versión`) por la codificación activa de esa consola. Es solo visual — el archivo `logs/ejecucion.log` siempre se escribe en UTF-8 correctamente.
