"""Orquestador de la automatización.

Este archivo debe leerse como el diagrama de docs/diseno/solucion.md: los
mismos pasos, en el mismo orden. Si no se parecen, uno de los dos está
desactualizado.

El detalle técnico vive en los conectores; acá solo está el flujo del negocio.
"""

from __future__ import annotations

import sys

from . import __version__
from .configuracion import Configuracion, cargar_configuracion
from .errores import ErrorAutomatizacion, ErrorConfiguracion, ErrorNegocio, ErrorSistema
from .modelos import EstadoItem, Item, Periodo, ResumenEjecucion
from .registro import configurar_registro, obtener_registro

registro = obtener_registro(__name__)


def obtener_items(configuracion: Configuracion, periodo: Periodo) -> list[Item]:
    """Obtiene la lista de trabajo de la corrida.

    Paso 1 del diagrama. Reemplazar por la lectura real: consulta al portal,
    archivo de entrada, cola de trabajo o lo que defina el relevamiento.
    """
    registro.info("Obteniendo ítems del período %s (entorno %s)", periodo, configuracion.entorno)
    return [Item(identificador=f"EJEMPLO-{n:03d}", periodo=periodo) for n in range(1, 4)]


def procesar_item(configuracion: Configuracion, item: Item) -> None:
    """Procesa un ítem de la lista de trabajo.

    Paso 2 del diagrama. Toda la lógica de un ítem va acá, de modo que un fallo
    afecte a ese ítem y no a la corrida completa.

    Raises:
        ErrorNegocio: si el ítem no puede procesarse por sus datos.
        ErrorSistema: ante una falla técnica transitoria.
    """
    registro.info(
        "Procesando %s con salida en %s", item.identificador, configuracion.carpeta_salida
    )
    # TODO: implementar el procesamiento real del ítem.


def informar_resultado(configuracion: Configuracion, resumen: ResumenEjecucion) -> None:
    """Deja el resultado donde lo espera el negocio.

    Paso 3 del diagrama: archivo de salida, correo, carga en el sistema destino.
    """
    destino = configuracion.carpeta_salida / f"resumen-{resumen.id_ejecucion}.txt"
    destino.write_text(str(resumen), encoding="utf-8")
    registro.info("Resultado de la corrida: %s (detalle en %s)", resumen, destino)


def ejecutar(periodo: Periodo | None = None) -> ResumenEjecucion:
    """Ejecuta la automatización completa y devuelve el resumen de la corrida.

    El procesamiento es por ítem: un `ErrorNegocio` marca el ítem como excepción
    y sigue; un `ErrorSistema` que sobrevive a los reintentos también corta solo
    ese ítem. Solo un error de configuración aborta la corrida entera.
    """
    id_ejecucion = configurar_registro()
    registro.info("=== Inicio de la corrida %s | versión %s ===", id_ejecucion, __version__)

    configuracion = cargar_configuracion()
    periodo = periodo or Periodo(anio=2026, mes=1)
    resumen = ResumenEjecucion(id_ejecucion=id_ejecucion)

    items = obtener_items(configuracion, periodo)
    registro.info("%s ítems a procesar", len(items))

    for item in items:
        try:
            procesar_item(configuracion, item)
            item.estado = EstadoItem.PROCESADO
        except ErrorNegocio as error:
            item.estado = EstadoItem.EXCEPCION_NEGOCIO
            item.detalle = str(error)
            registro.warning("Excepción de negocio en %s: %s", item.identificador, error)
        except ErrorSistema as error:
            item.estado = EstadoItem.ERROR_SISTEMA
            item.detalle = str(error)
            registro.error("Error de sistema en %s: %s", item.identificador, error)
        resumen.items.append(item)

    informar_resultado(configuracion, resumen)
    registro.info("=== Fin de la corrida %s | %s ===", id_ejecucion, resumen)
    return resumen


def main() -> int:
    """Punto de entrada. Devuelve el código de salida del proceso.

    0 = todo procesado · 1 = hubo errores de sistema · 2 = error de configuración
    """
    try:
        resumen = ejecutar()
    except ErrorConfiguracion as error:
        registro.critical("Error de configuración: %s", error)
        return 2
    except ErrorAutomatizacion as error:
        registro.critical("La corrida se abortó: %s", error)
        return 1
    except Exception:
        registro.critical("Error inesperado. Detalle completo:", exc_info=True)
        return 1
    return 1 if resumen.errores_sistema else 0


if __name__ == "__main__":
    sys.exit(main())
