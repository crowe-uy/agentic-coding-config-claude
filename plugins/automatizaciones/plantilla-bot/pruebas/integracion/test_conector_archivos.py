"""Pruebas del conector de archivos contra archivos reales en carpeta temporal."""

from pathlib import Path

import pytest

from paquete_bot.conectores.archivos import ConectorArchivos, leer_csv_validado
from paquete_bot.errores import ErrorNegocio, ErrorSistema

COLUMNAS = ["identificador", "periodo", "destino"]


@pytest.mark.caso("CP-009")
def test_lee_un_csv_valido(csv_de_ejemplo: Path) -> None:
    """Un CSV con las columnas esperadas se lee completo."""
    # Ejecutar
    filas = leer_csv_validado(csv_de_ejemplo, COLUMNAS)

    # Verificar
    assert len(filas) == 2
    assert filas[0]["identificador"] == "EJEMPLO-001"


@pytest.mark.caso("CP-010")
def test_rechaza_csv_con_columna_faltante(carpeta_temporal: Path) -> None:
    """Una columna renombrada da un ErrorNegocio que nombra la columna faltante."""
    # Preparar
    ruta = carpeta_temporal / "mal.csv"
    ruta.write_text("identificador,periodo\nEJEMPLO-001,2026-01\n", encoding="utf-8")

    # Ejecutar y verificar
    with pytest.raises(ErrorNegocio, match="destino"):
        leer_csv_validado(ruta, COLUMNAS)


@pytest.mark.caso("CP-011")
def test_rechaza_csv_sin_filas(carpeta_temporal: Path) -> None:
    """Un archivo con encabezado pero sin datos es una excepción de negocio."""
    # Preparar
    ruta = carpeta_temporal / "vacio.csv"
    ruta.write_text("identificador,periodo,destino\n", encoding="utf-8")

    # Ejecutar y verificar
    with pytest.raises(ErrorNegocio, match="no tiene filas"):
        leer_csv_validado(ruta, COLUMNAS)


@pytest.mark.caso("CP-012")
def test_carpeta_inaccesible_es_error_de_sistema(carpeta_temporal: Path) -> None:
    """Una carpeta de red caída es ErrorSistema, y por lo tanto se reintenta."""
    # Preparar
    conector = ConectorArchivos(carpeta_temporal / "no-existe")

    # Ejecutar y verificar
    with pytest.raises(ErrorSistema, match="no está accesible"):
        conector.conectar()


@pytest.mark.caso("CP-013")
def test_el_conector_cierra_aunque_falle(conector_falso) -> None:  # noqa: ANN001
    """El gestor de contexto desconecta incluso si el bloque lanza una excepción."""
    # Ejecutar
    with pytest.raises(ValueError), conector_falso:
        raise ValueError("falla simulada")

    # Verificar
    assert conector_falso.llamadas == ["conectar", "desconectar"]
    assert conector_falso.conectado is False
