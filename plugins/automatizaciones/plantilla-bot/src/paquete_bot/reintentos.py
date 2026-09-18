"""Reintentos con espera creciente y esperas por condición.

Regla del equipo: solo se reintentan los `ErrorSistema`. Un `ErrorNegocio`
reintentado es tiempo perdido contra un dato que nunca va a estar bien.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from functools import wraps
from typing import TypeVar

from .errores import ErrorSistema
from .registro import obtener_registro

registro = obtener_registro(__name__)

T = TypeVar("T")


def con_reintentos(
    intentos: int = 3,
    espera_inicial: float = 2.0,
    factor: float = 2.0,
    errores: tuple[type[Exception], ...] = (ErrorSistema,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Reintenta la función ante los errores indicados, con espera creciente.

    La espera arranca en `espera_inicial` segundos y se multiplica por `factor`
    en cada intento fallido. Si se agotan los intentos, propaga la excepción.
    """

    def decorador(funcion: Callable[..., T]) -> Callable[..., T]:
        @wraps(funcion)
        def envoltorio(*args: object, **kwargs: object) -> T:
            espera = espera_inicial
            for intento in range(1, intentos + 1):
                try:
                    return funcion(*args, **kwargs)
                except errores as error:
                    if intento == intentos:
                        registro.error(
                            "%s falló tras %s intentos: %s", funcion.__name__, intentos, error
                        )
                        raise
                    registro.warning(
                        "%s falló (intento %s/%s): %s. Reintenta en %.1fs",
                        funcion.__name__,
                        intento,
                        intentos,
                        error,
                        espera,
                    )
                    time.sleep(espera)
                    espera *= factor
            raise AssertionError("inalcanzable")  # pragma: no cover

        return envoltorio

    return decorador


def esperar_hasta(
    condicion: Callable[[], bool],
    tiempo_maximo: float = 30.0,
    intervalo: float = 0.5,
    descripcion: str = "la condición esperada",
) -> None:
    """Espera hasta que `condicion` sea verdadera o se agote el tiempo.

    Reemplaza a `time.sleep()` para esperar a que algo aparezca o termine.

    Raises:
        ErrorSistema: si se agota el tiempo sin que se cumpla la condición.
    """
    limite = time.monotonic() + tiempo_maximo
    while time.monotonic() < limite:
        if condicion():
            return
        time.sleep(intervalo)
    raise ErrorSistema(f"Se agotaron {tiempo_maximo:.0f}s esperando {descripcion}.")
