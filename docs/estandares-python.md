# Estándares de código Python para automatizaciones

A diferencia de una herramienta de RPA, acá nada es implícito: reintentos, esperas, manejo de errores y trazabilidad se escriben a mano. Por eso se escriben siempre igual.

## Nombres

En español, sin tildes ni `ñ` en identificadores. Los textos visibles (docstrings, logs, mensajes) sí llevan tildes.

```python
def validar_periodo(anio: int, mes: int) -> None:
    """Valida que el período solicitado sea procesable."""
    if not 1 <= mes <= 12:
        raise ErrorNegocio(f"El mes {mes} no es válido.")
```

- Módulos y funciones: `snake_case` — `descargar_comprobantes`, `conectores/portal_web.py`
- Clases y excepciones: `PascalCase` — `ConectorPortal`, `ErrorNegocio`
- Constantes: `MAYUSCULAS` — `INTENTOS_MAXIMOS`
- Funciones que devuelven booleano empiezan con verbo: `existe_archivo`, `esta_vencido`

## Estructura del proyecto

```
src/paquete_bot/
├── principal.py        Orquestador: el flujo del diagrama, leído de arriba a abajo
├── configuracion.py    Carga .env y parametrizaciones; falla temprano si falta algo
├── registro.py         Logging con id de ejecución, a consola y archivo rotativo
├── errores.py          Jerarquía de excepciones
├── reintentos.py       Decorador de reintentos con espera creciente
├── modelos.py          Estructuras de datos del dominio (dataclasses)
└── conectores/         Un módulo por sistema externo
```

`principal.py` se lee como el diagrama de la solución. Si no se parecen, uno de los dos está desactualizado.

## Errores: negocio vs. sistema

Toda excepción hereda de una de estas dos:

```python
class ErrorAutomatizacion(Exception):
    """Base de todos los errores propios del bot."""


class ErrorNegocio(ErrorAutomatizacion):
    """El dato o la situación no permiten continuar. NO se reintenta.

    Ejemplos: factura duplicada, CUIT inválido, período ya procesado.
    Se registra, se reporta y el ítem se marca como excepción de negocio.
    """


class ErrorSistema(ErrorAutomatizacion):
    """Falla técnica transitoria. SÍ se reintenta.

    Ejemplos: timeout, portal caído, sesión expirada, archivo bloqueado.
    """
```

Clasificar mal es la causa más común de bots frágiles: reintentar un `ErrorNegocio` es insistir contra un dato que nunca va a estar bien; no reintentar un `ErrorSistema` es abortar por un parpadeo de red.

Nunca `except:` desnudo ni `except Exception: pass`. Si se ignora una excepción a propósito, se comenta por qué:

```python
try:
    navegador.cerrar_aviso_cookies()
except ElementoNoEncontrado:
    pass  # El aviso solo aparece en la primera visita del día.
```

## Reintentos y esperas

```python
@con_reintentos(intentos=3, espera_inicial=2.0, errores=(ErrorSistema,))
def descargar_comprobante(numero: str) -> Path: ...
```

El decorador solo reintenta `ErrorSistema`, con espera creciente. Nunca `time.sleep()` fijo para esperar algo: se espera por la condición.

```python
# Mal: frágil y lento
time.sleep(5)
boton.click()

# Bien: espera por la condición real
esperar_hasta(lambda: boton.esta_visible(), tiempo_maximo=30)
boton.click()
```

`time.sleep()` solo es válido para respetar un límite de frecuencia de un sistema externo, con un comentario que lo explique.

## Conectores

Cada sistema externo (portal web, SAP, API, carpeta de red, correo) va detrás de un conector con interfaz propia. Nunca se llama a Playwright, pywinauto o `requests` desde `principal.py`.

```python
class ConectorPortal(Protocol):
    def iniciar_sesion(self) -> None: ...
    def buscar_comprobantes(self, periodo: Periodo) -> list[Comprobante]: ...
    def descargar(self, comprobante: Comprobante) -> Path: ...
```

Así el flujo se lee sin ruido técnico, se puede probar con un conector falso sin abrir un navegador, y un cambio en el portal toca un solo archivo.

Todo conector usa gestión de contexto (`with`) para cerrar sesiones, navegadores y archivos aunque haya una excepción.

## Registro y evidencia

- Id de ejecución en cada línea de log.
- Consola + archivo rotativo en `logs/`.
- `INFO` para hitos del flujo, `DEBUG` para detalle técnico, `WARNING` para reintentos, `ERROR` para lo que aborta un ítem.
- Nunca se loguea una credencial, ni en `DEBUG`.
- Ante un error, captura de pantalla automática en `logs/capturas/<id_ejecucion>/`.

```python
registro.info("Procesando comprobante %s de %s", indice, total)
registro.warning("Reintento %s/%s tras timeout del portal", intento, intentos)
```

## Configuración y parametrización

Dos cosas distintas:

- **Configuración**: lo que cambia por entorno y es sensible → `.env` (usuarios, claves, URLs, rutas).
- **Parametrización**: lo que cambia por operación y maneja el usuario → Excel o CSV en `datos/`, documentado en el manual.

`configuracion.py` valida todo al arrancar, antes de abrir nada — no a mitad de la corrida.

```python
def cargar_configuracion() -> Configuracion:
    """Carga y valida la configuración. Falla inmediatamente si algo falta."""
```

Las parametrizaciones se validan al leerlas: columnas esperadas, tipos, valores obligatorios. Una columna renombrada da un error claro, no un `KeyError` a mitad del proceso.

## Idempotencia y reanudación

Dos preguntas a responder en el diseño y resolver en el código:

1. **¿Qué pasa si se ejecuta dos veces sobre el mismo período?** No debe duplicar cargas ni correos.
2. **¿Qué pasa si se cae en el ítem 300 de 500?** Debe retomar sin reprocesar lo hecho.

Forma habitual: procesar por ítem, registrar el resultado de cada uno (archivo de estado o sistema destino) y consultar ese registro al iniciar.

## Estilo

`ruff` formatea y revisa en cada edición, configurado en `pyproject.toml`:

- Línea de 100 caracteres.
- Reglas `E, F, I, B, UP, SIM, RET, ARG, PTH, N`.
- Tipado en firmas públicas.
- Docstring en español por módulo, clase y función pública: qué hace, qué excepciones lanza.
- Funciones de una sola responsabilidad. Si necesita comentarios de sección para entenderse, son varias funciones.
- Rutas con `pathlib.Path`, nunca concatenando cadenas.

## Pruebas

| Carpeta | Qué prueba | Depende de |
|---|---|---|
| `pruebas/unitarias/` | Reglas de negocio, validaciones, transformaciones | Nada externo |
| `pruebas/integracion/` | Conectores contra dobles o servidores falsos | Sin sistemas reales |
| `pruebas/e2e/` | Flujo completo, marcado `@pytest.mark.e2e` | Entorno real; se corre en el release |

- Una prueba por caso del catálogo, con `@pytest.mark.caso("CP-007")`.
- Nombres que describen el escenario: `test_rechaza_comprobante_con_cuit_invalido`.
- Patrón preparar / ejecutar / verificar, visible en el cuerpo.
- Se prueban los bordes y los errores, no solo el camino feliz: ahí está casi toda la falla real.
- Nada de red ni interfaz gráfica en `unitarias/`: si necesita un navegador, es de integración o e2e.

Si cambia el código, cambian las pruebas. Un PR que modifica comportamiento sin tocar pruebas se rechaza.
