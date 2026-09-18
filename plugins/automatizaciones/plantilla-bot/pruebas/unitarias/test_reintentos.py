"""Pruebas de la política de reintentos.

Son las pruebas más importantes de la plantilla: verifican la regla que
distingue un bot robusto de uno frágil.
"""

import pytest

from paquete_bot.errores import ErrorNegocio, ErrorSistema
from paquete_bot.reintentos import con_reintentos, esperar_hasta


@pytest.mark.caso("CP-004")
def test_reintenta_el_error_de_sistema_hasta_lograrlo() -> None:
    """Un ErrorSistema transitorio se reintenta y termina bien."""
    # Preparar
    intentos = {"contador": 0}

    @con_reintentos(intentos=3, espera_inicial=0.01)
    def operacion_inestable() -> str:
        intentos["contador"] += 1
        if intentos["contador"] < 3:
            raise ErrorSistema("El portal no responde")
        return "listo"

    # Ejecutar
    resultado = operacion_inestable()

    # Verificar
    assert resultado == "listo"
    assert intentos["contador"] == 3


@pytest.mark.caso("CP-005")
def test_no_reintenta_el_error_de_negocio() -> None:
    """Un ErrorNegocio se propaga en el primer intento: reintentarlo es inútil."""
    # Preparar
    intentos = {"contador": 0}

    @con_reintentos(intentos=3, espera_inicial=0.01)
    def dato_invalido() -> None:
        intentos["contador"] += 1
        raise ErrorNegocio("El CUIT no es válido")

    # Ejecutar y verificar
    with pytest.raises(ErrorNegocio):
        dato_invalido()
    assert intentos["contador"] == 1


@pytest.mark.caso("CP-006")
def test_agota_los_intentos_y_propaga() -> None:
    """Si el error de sistema persiste, se propaga tras el último intento."""
    # Preparar
    intentos = {"contador": 0}

    @con_reintentos(intentos=2, espera_inicial=0.01)
    def siempre_falla() -> None:
        intentos["contador"] += 1
        raise ErrorSistema("Timeout")

    # Ejecutar y verificar
    with pytest.raises(ErrorSistema):
        siempre_falla()
    assert intentos["contador"] == 2


@pytest.mark.caso("CP-007")
def test_esperar_hasta_devuelve_al_cumplirse_la_condicion() -> None:
    """La espera termina apenas la condición es verdadera."""
    # Preparar
    llamadas = {"contador": 0}

    def ya_cargo() -> bool:
        llamadas["contador"] += 1
        return llamadas["contador"] >= 2

    # Ejecutar
    esperar_hasta(ya_cargo, tiempo_maximo=2, intervalo=0.01)

    # Verificar
    assert llamadas["contador"] == 2


@pytest.mark.caso("CP-008")
def test_esperar_hasta_agota_el_tiempo() -> None:
    """Si la condición nunca se cumple, lanza ErrorSistema con el detalle."""
    # Ejecutar y verificar
    with pytest.raises(ErrorSistema, match="esperando"):
        esperar_hasta(
            lambda: False,
            tiempo_maximo=0.05,
            intervalo=0.01,
            descripcion="el menú principal",
        )
