# Manual de usuario — <NOMBRE_DEL_BOT>

**Dirigido al equipo de mantenimiento de la automatización.** Describe qué hace el bot, qué necesita para correr, qué deja al terminar, qué se puede parametrizar y qué hacer cuando algo falla.

| | |
|---|---|
| **Versión del manual** | 1.0 |
| **Versión del bot** | 1.0.0 |
| **Fecha** | AAAA-MM-DD |
| **Responsable** | |
| **Referente técnico** | |

## Qué hace la automatización

Descripción en lenguaje de negocio, entendible por alguien que no la desarrolló. Qué proceso reemplaza, con qué frecuencia corre y quién usa su resultado. Tres o cuatro oraciones.

**Diagrama del flujo:** [docs/diseno/solucion.md](diseno/solucion.md)

## Precondiciones

Todo lo que debe cumplirse **antes** de ejecutar. Si algo de esta lista falla, el bot no debe arrancar.

### Del equipo donde corre

| Requisito | Detalle | Cómo verificarlo |
|---|---|---|
| Sistema operativo | Windows 10/11 | |
| Python | 3.14 | `python --version` |
| Software adicional | | |
| Espacio en disco | | |

### De los sistemas externos

| Sistema | Debe estar | Cómo verificarlo | Qué hacer si no |
|---|---|---|---|
| | disponible y con sesión habilitada | | |

### De los datos de entrada

| Entrada | Ubicación | Formato exigido | Quién la deja |
|---|---|---|---|
| | | | |

### De las credenciales

| Credencial | Variable en `.env` | Quién la provee | Cada cuánto vence |
|---|---|---|---|
| Usuario del portal | `PORTAL_USUARIO` | | |
| Clave del portal | `PORTAL_CLAVE` | | |

> Las credenciales **no** están en el repositorio. Viven en el archivo `.env` del equipo donde corre el bot. Si vencen, el bot falla con `ErrorConfiguracion` o con un error de login, y se resuelve actualizando el `.env`.

## Postcondiciones y resultados

Qué deja la automatización cuando termina bien.

| Resultado | Dónde queda | Formato | Cómo verificarlo |
|---|---|---|---|
| | | | |

### Registro de la corrida

| | |
|---|---|
| **Log de ejecución** | `logs/ejecucion.log` (rotativo, 10 archivos) |
| **Capturas de error** | `logs/capturas/<id_ejecucion>/` |
| **Resumen de la corrida** | `<carpeta de salida>/resumen-<id_ejecucion>.txt` |

Cada línea del log lleva el **id de ejecución**: para investigar una corrida puntual, se filtra el log por ese id.

### Códigos de salida

| Código | Significado | Qué hacer |
|---|---|---|
| 0 | Todo procesado correctamente | Nada |
| 1 | Hubo errores de sistema | Revisar el log y reejecutar |
| 2 | Error de configuración | Revisar el `.env` y las precondiciones |

### ¿Se puede volver a ejecutar?

Sí / No, y por qué. Qué pasa si se ejecuta dos veces sobre el mismo período: si duplica algo, decirlo explícitamente y aclarar qué hay que limpiar antes de reejecutar.

## Parametrizaciones

Lo que el equipo de mantenimiento **puede cambiar sin tocar el código**.

### Archivos parametrizables

| Archivo | Ubicación | Quién lo mantiene | Cuándo se modifica |
|---|---|---|---|
| `parametros.csv` | `datos/` | | |

#### `parametros.csv`

| Columna | Tipo | Obligatoria | Validación | Ejemplo |
|---|---|---|---|---|
| `identificador` | texto | sí | No vacío | `EJEMPLO-001` |
| `periodo` | texto `AAAA-MM` | sí | Mes entre 01 y 12 | `2026-01` |
| `destino` | texto | sí | Debe existir en la lista de destinos | `casilla-a` |

**Reglas al modificarlo:** no renombrar ni reordenar columnas (el bot valida los nombres y aborta con un error claro si no coinciden), guardar en UTF-8, y no dejar filas vacías al final.

### Variables de entorno

| Variable | Qué configura | Ejemplo | Cambiarla requiere |
|---|---|---|---|
| `ENTORNO` | Ambiente de ejecución | `produccion` | reinicio |
| `PORTAL_URL` | Dirección del portal | | reinicio |
| `CARPETA_SALIDA` | Dónde deja los resultados | | reinicio |

El archivo `.env.example` del repositorio lista todas las variables sin sus valores.

## Errores contemplados

Errores que el bot **maneja solo**. Aparecen en el log y no requieren intervención salvo que se repitan.

| Código | Mensaje en el log | Causa | Qué hace el bot | Acción del soporte |
|---|---|---|---|---|
| E-001 | `Excepción de negocio en <ítem>` | El ítem no cumple una regla de negocio | Lo marca como excepción y sigue con el próximo | Revisar el ítem con el usuario del negocio |
| E-002 | `Error de sistema en <ítem>` | Falla técnica que sobrevivió a los reintentos | Marca el ítem y sigue | Verificar el sistema externo y reejecutar solo ese ítem |
| E-003 | `Error de configuración` | Falta una variable de entorno o una ruta | Aborta antes de empezar | Completar el `.env` según la tabla de precondiciones |
| E-004 | `Al archivo X le faltan columnas` | La parametrización fue modificada incorrectamente | Aborta antes de procesar | Restaurar las columnas originales |

## Errores conocidos

Problemas detectados que **no** tienen solución dentro de la automatización. Se documentan para que el soporte no los investigue dos veces.

| # | Síntoma | Cómo replicarlo | Causa | ¿Tiene solución? | Responsable |
|---|---|---|---|---|---|
| EC-001 | | Pasos exactos para reproducirlo | | Sí, ver workaround / No, es del cliente | Equipo de automatización / Cliente / Proveedor del sistema |

**Responsable** indica quién debe resolverlo, no quién lo detectó. Si la causa está en un sistema del cliente (portal que cambia sin aviso, permisos que se revocan, datos mal cargados), se declara como responsabilidad del cliente y se acuerda el procedimiento.

## Cómo ejecutar la automatización

**Forma de distribución:** código fuente (requiere Python instalado) / `.exe` empaquetado con PyInstaller — completar según corresponda a este bot. <!-- borrar la que no aplique -->

### Manualmente — código fuente

```bash
cd <carpeta del bot>
.venv\Scripts\activate
python ejecutar.py
```

### Manualmente — `.exe`

```bash
cd <carpeta con el .exe>
<paquete>-X.Y.Z.exe
```

El `.env` (o `.env.local`/`.env.dev`) tiene que estar **en la misma carpeta que el `.exe`**: ahí es donde el bot busca todo (credenciales, `logs/`, `salida/`), sin importar desde dónde se lo invoque. Ver `docs/empaquetado` del plugin.

### Programada

**Mecanismo:** Programador de tareas de Windows / orquestador.

Una fila por tarea programada — un bot de una sola etapa tiene una sola fila; un bot con etapas separadas (ver `docs/diseno/solucion.md`) tiene una por etapa, cada una invocando el mismo `.exe` con un argumento distinto.

| Etapa / tarea | Frecuencia | Horario | Usuario que la ejecuta | Argumento |
|---|---|---|---|---|
| | | | | |

### Reconstruir el `.exe` (si aplica)

Solo si este bot se distribuye empaquetado. `/empaquetar` en el plugin del equipo hace todo el proceso; en resumen: `pip install -r requirements.txt -r requirements-dev.txt` (incluye PyInstaller), `pyinstaller paquete.spec`, y renombrar el resultado con la versión del release.

### Cómo detenerla

Qué pasa si se interrumpe a mitad de una corrida y qué hay que verificar antes de volver a lanzarla.

## Contactos

| Rol | Nombre | Cuándo contactarlo |
|---|---|---|
| Desarrollador | | Errores del bot |
| Referente técnico | | Cambios de alcance |
| Referente del negocio | | Dudas sobre reglas o datos |
| Soporte del sistema externo | | Caídas del portal, permisos |

## Versiones del manual

| Versión del manual | Versión del bot | Fecha | Cambios | Autor |
|---|---|---|---|---|
| 1.0 | 1.0.0 | AAAA-MM-DD | Versión inicial | |
