"""Conector a archivos y carpetas: CSV, Excel y carpetas de red.

Las parametrizaciones se validan al leerlas. Un archivo con una columna
renombrada tiene que dar un error claro, no un KeyError a mitad del proceso.
"""

from __future__ import annotations

import csv
from pathlib import Path

from ..errores import ErrorNegocio, ErrorSistema
from ..registro import obtener_registro
from .base import Conector

registro = obtener_registro(__name__)


class ConectorArchivos(Conector):
    """Acceso a una carpeta de trabajo local o de red."""

    nombre = "archivos"

    def __init__(self, carpeta: Path) -> None:
        self.carpeta = carpeta

    def conectar(self) -> None:
        """Verifica que la carpeta esté accesible.

        Raises:
            ErrorSistema: si la carpeta de red no responde.
        """
        if not self.carpeta.exists():
            raise ErrorSistema(f"La carpeta {self.carpeta} no está accesible.")

    def desconectar(self) -> None:
        """No hay recursos que liberar."""

    def listar(self, patron: str = "*") -> list[Path]:
        """Lista los archivos de la carpeta que coinciden con el patrón."""
        return sorted(self.carpeta.glob(patron))


def leer_csv_validado(ruta: Path, columnas_esperadas: list[str]) -> list[dict[str, str]]:
    """Lee un CSV verificando que tenga las columnas esperadas.

    Raises:
        ErrorNegocio: si faltan columnas o el archivo no tiene filas.
        ErrorSistema: si el archivo no se puede abrir.
    """
    try:
        with ruta.open(encoding="utf-8-sig", newline="") as archivo:
            lector = csv.DictReader(archivo)
            columnas = lector.fieldnames or []
            faltantes = [c for c in columnas_esperadas if c not in columnas]
            if faltantes:
                raise ErrorNegocio(
                    f"Al archivo {ruta.name} le faltan columnas: {', '.join(faltantes)}. "
                    f"Columnas encontradas: {', '.join(columnas)}."
                )
            filas = list(lector)
    except OSError as error:
        raise ErrorSistema(f"No se pudo leer {ruta}: {error}") from error

    if not filas:
        raise ErrorNegocio(f"El archivo {ruta.name} no tiene filas para procesar.")

    registro.info("Leídas %s filas de %s", len(filas), ruta.name)
    return filas
