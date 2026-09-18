"""Pruebas del conector web: qué navegador elige según el canal pedido.

No requieren Playwright instalado: _opciones_lanzamiento es una función pura,
separada a propósito para poder probar esta lógica sin abrir un navegador.
"""

import pytest

from paquete_bot.conectores.web import _opciones_lanzamiento


@pytest.mark.caso("CP-029")
def test_sin_canal_usa_el_chromium_propio_de_playwright() -> None:
    """Por defecto (canal=None) no se pide un canal: Playwright usa su Chromium."""
    # Ejecutar y verificar
    assert _opciones_lanzamiento(visible=False, canal=None) == {"headless": True}


@pytest.mark.caso("CP-030")
def test_canal_msedge_usa_el_edge_del_sistema() -> None:
    """Con canal='msedge', se pide ese canal: usa el Edge ya instalado en Windows."""
    # Ejecutar y verificar
    opciones = _opciones_lanzamiento(visible=False, canal="msedge")

    assert opciones == {"headless": True, "channel": "msedge"}


@pytest.mark.caso("CP-031")
def test_visible_desactiva_headless() -> None:
    """visible=True corre con ventana, para depurar en desarrollo."""
    # Ejecutar y verificar
    assert _opciones_lanzamiento(visible=True, canal=None) == {"headless": False}
