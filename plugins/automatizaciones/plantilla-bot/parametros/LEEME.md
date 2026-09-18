# Parámetros

Lo que el usuario puede cambiar sin tocar el código: qué procesar, con qué valores, hacia dónde.

| Carpeta / variable | Qué es | ¿Va al repositorio? |
|---|---|---|
| `ejemplo/` | Parametrizaciones de ejemplo con **datos ficticios**. Solo para pruebas y como referencia del formato — la corrida real nunca lee de acá. | Sí |
| `reales/` | Parametrización real, cuando vive en este mismo equipo (caso menos común). | **No**, ignorada por git |
| `CARPETA_PARAMETROS` (`.env`) | Lo más habitual: la parametrización real vive en una **carpeta compartida de red** que edita el cliente directamente — no en este repositorio. Esta variable apunta ahí. | No aplica (es una ruta externa) |

Antes de commitear un archivo en `ejemplo/`, verificá que no contenga CUIT, DNI, montos, nombres de personas ni razones sociales reales.

Ver también `CARPETA_ENTRADA` en `.env.example`: es distinta de `CARPETA_PARAMETROS` — son las planillas u otros archivos que el cliente deja **para que el bot los procese** en cada corrida (el trabajo en sí), no configuración de cómo se comporta el bot.
