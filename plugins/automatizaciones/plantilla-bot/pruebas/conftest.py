"""Fixtures compartidas por todas las pruebas."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from paquete_bot.conectores.base import Conector


@pytest.fixture
def carpeta_temporal(tmp_path: Path) -> Path:
    """Carpeta de trabajo aislada para la prueba."""
    return tmp_path


@pytest.fixture
def csv_de_ejemplo(tmp_path: Path) -> Path:
    """CSV de parametrización válido, con datos ficticios."""
    ruta = tmp_path / "parametros.csv"
    with ruta.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=["identificador", "periodo", "destino"])
        escritor.writeheader()
        escritor.writerow(
            {"identificador": "EJEMPLO-001", "periodo": "2026-01", "destino": "casilla-a"}
        )
        escritor.writerow(
            {"identificador": "EJEMPLO-002", "periodo": "2026-01", "destino": "casilla-b"}
        )
    return ruta


class ConectorFalso(Conector):
    """Doble de prueba: registra las llamadas sin tocar ningún sistema real.

    Permite probar el flujo completo sin abrir un navegador ni una aplicación.
    """

    nombre = "falso"

    def __init__(self) -> None:
        self.conectado = False
        self.llamadas: list[str] = []

    def conectar(self) -> None:
        self.conectado = True
        self.llamadas.append("conectar")

    def desconectar(self) -> None:
        self.conectado = False
        self.llamadas.append("desconectar")


@pytest.fixture
def conector_falso() -> ConectorFalso:
    """Conector de prueba para verificar el flujo sin sistemas externos."""
    return ConectorFalso()
