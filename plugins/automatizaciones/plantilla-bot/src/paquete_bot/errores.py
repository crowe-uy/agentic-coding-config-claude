"""Jerarquía de excepciones de la automatización.

La distinción entre error de negocio y error de sistema es la decisión de diseño
más importante del bot: determina qué se reintenta y qué no.
"""


class ErrorAutomatizacion(Exception):
    """Base de todos los errores propios de la automatización."""


class ErrorNegocio(ErrorAutomatizacion):
    """El dato o la situación no permiten continuar. NO se reintenta.

    Ejemplos: comprobante duplicado, CUIT inválido, período ya procesado,
    archivo de entrada con una columna faltante.

    El ítem se marca como excepción de negocio y el proceso continúa con el
    siguiente. Reintentar no cambiaría el resultado.
    """


class ErrorSistema(ErrorAutomatizacion):
    """Falla técnica transitoria. SÍ se reintenta.

    Ejemplos: timeout de red, portal caído, sesión expirada, archivo bloqueado
    por otro proceso, ventana que todavía no cargó.
    """


class ErrorConfiguracion(ErrorAutomatizacion):
    """Falta o es inválida una variable de entorno o una parametrización.

    Se detecta al arrancar, antes de abrir cualquier sistema externo. No se
    reintenta: requiere intervención humana.
    """
