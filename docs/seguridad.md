# Seguridad e información sensible

## Regla

**Nada sensible entra al repositorio.** Ni en el código, ni en los commits, ni en la documentación, ni en las capturas de evidencia. Un secreto commiteado y después borrado **sigue estando** en el historial.

## Qué se considera sensible

| Categoría | Ejemplos | Dónde va |
|---|---|---|
| Documento de relevamiento | `.docx`, `.pdf` del cliente | Carpeta local `relevamiento/`, ignorada por git |
| Credenciales | Usuarios, contraseñas, tokens, API keys, cadenas de conexión | `.env.local` / `.env.dev` / `.env` local; documentadas sin valor en `.env.example` |
| Certificados y llaves | `.pem`, `.pfx`, `.key` | Fuera del repositorio |
| Datos reales | Planillas con CUIT, DNI, montos, nombres de clientes | `datos/reales/` (ignorada). Al repo va `datos/ejemplo/` con datos ficticios |
| Infraestructura interna | IPs, rutas UNC, nombres de servidores, URLs internas con token | Parametrizadas en `.env`, referidas de forma genérica en la documentación |
| Evidencia de pruebas | Capturas con datos de producción | Se anonimiza antes de commitear |

## Manejo de credenciales

Un único `.env.example` versionado documenta **cada variable sin su valor**:

```
# Portal de proveedores
PORTAL_URL=
PORTAL_USUARIO=
PORTAL_CLAVE=

# Casilla de notificaciones
SMTP_SERVIDOR=
SMTP_USUARIO=
SMTP_CLAVE=
```

Los valores reales van en un archivo local que **nunca se versiona** (el `.gitignore` de la plantilla excluye cualquier `.env.*` salvo `.env.example`). Tres nombres posibles, según el caso — `cargar_configuracion()` busca en este orden y usa el primero que encuentra:

| Archivo | Para qué |
|---|---|
| `.env.local` | Tus credenciales, solo en tu máquina. Lo normal durante la Fase 2. |
| `.env.dev` | Credenciales de desarrollo compartidas por el equipo. |
| `.env` | El que usa la ejecución real: programada o manual, en el equipo donde corre el bot. |

Toda variable que el código lea con `obtener_variable(...)` debe existir en `.env.example`: el verificador del ciclo lo comprueba y rechaza el release si falta alguna.

En el manual de usuario se documenta **qué credencial necesita el bot y quién la provee**, nunca su valor.

> Cuando la empresa disponga de un gestor central (Azure Key Vault, CyberArk o similar), la migración solo toca `configuracion.py`: el resto del código sigue pidiendo las credenciales por nombre.

## Controles automáticos

Tres capas, de menos a más estricta:

1. **`.gitignore`** — excluye `relevamiento/`, cualquier `.env.*` (menos `.env.example`), `datos/reales/`, certificados y logs.
2. **Guardia del agente** (`guardia_secretos.py`) — impide que Claude escriba en rutas prohibidas, que agregue al índice archivos sensibles o que introduzca secretos en el contenido de un archivo.
3. **Control previo al commit** (`pre-commit` de git) — escanea el diff en el índice buscando patrones de secreto y alta entropía. Actúa aunque el desarrollador commitee a mano, sin Claude.

### Si el control bloquea algo que no es un secreto

Suele pasar con datos de prueba o ejemplos de documentación. Revisá primero que realmente no lo sea, y si es un falso positivo agregá `# escaneo-ok: motivo` en la misma línea: el escáner lo omite y el motivo queda visible en la revisión del PR.

## Si se filtró un secreto

1. **Rotar la credencial inmediatamente.** Es lo primero y lo único urgente: mientras la credencial sea válida, sigue expuesta.
2. Avisar al referente técnico.
3. Limpiar el historial (`git filter-repo` o soporte de GitHub) y forzar el cambio coordinando con el equipo.
4. Registrar el incidente en la bitácora: qué se filtró, cómo, qué se hizo.

Borrar el archivo en un commit nuevo **no** resuelve nada por sí solo.
