"""Pruebas de las estructuras del dominio."""

import pytest

from paquete_bot.modelos import EstadoItem, Item, Periodo, ResumenEjecucion


@pytest.mark.caso("CP-001")
def test_periodo_rechaza_mes_invalido() -> None:
    """Un mes fuera de 1-12 no debe poder construirse."""
    # Ejecutar y verificar
    with pytest.raises(ValueError, match="Mes inválido"):
        Periodo(anio=2026, mes=13)


@pytest.mark.caso("CP-002")
def test_periodo_se_formatea_con_ceros() -> None:
    """El período se muestra siempre como AAAA-MM."""
    # Preparar
    periodo = Periodo(anio=2026, mes=3)

    # Ejecutar y verificar
    assert str(periodo) == "2026-03"


@pytest.mark.caso("CP-003")
def test_resumen_cuenta_cada_estado() -> None:
    """El resumen de la corrida totaliza por estado."""
    # Preparar
    periodo = Periodo(anio=2026, mes=1)
    resumen = ResumenEjecucion(id_ejecucion="prueba")
    resumen.items = [
        Item("A", periodo, estado=EstadoItem.PROCESADO),
        Item("B", periodo, estado=EstadoItem.EXCEPCION_NEGOCIO),
        Item("C", periodo, estado=EstadoItem.ERROR_SISTEMA),
        Item("D", periodo, estado=EstadoItem.PROCESADO),
    ]

    # Verificar
    assert resumen.procesados == 2
    assert resumen.excepciones_negocio == 1
    assert resumen.errores_sistema == 1
