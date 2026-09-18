"""Registro de ejecución: consola + archivo rotativo, con id de corrida.

Cada línea de log lleva el id de la ejecución, de modo que una corrida completa
puede seguirse entre miles de líneas.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

FORMATO = "%(asctime)s | %(id_ejecucion)s | %(levelname)-8s | %(name)s | %(message)s"

_id_ejecucion = ""


def generar_id_ejecucion() -> str:
    """Genera el identificador único de esta corrida."""
    return f"{datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:6]}"


class _FiltroIdEjecucion(logging.Filter):
    """Agrega el id de ejecución a cada registro."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.id_ejecucion = _id_ejecucion or "sin-id"
        return True


def configurar_registro(
    carpeta_logs: Path = Path("logs"),
    nivel: int = logging.INFO,
    id_ejecucion: str | None = None,
) -> str:
    """Configura el registro global y devuelve el id de ejecución.

    Debe llamarse una sola vez, al inicio de la corrida.
    """
    global _id_ejecucion
    _id_ejecucion = id_ejecucion or generar_id_ejecucion()

    carpeta_logs.mkdir(parents=True, exist_ok=True)
    formateador = logging.Formatter(FORMATO)
    filtro = _FiltroIdEjecucion()

    consola = logging.StreamHandler()
    consola.setFormatter(formateador)
    consola.addFilter(filtro)

    archivo = RotatingFileHandler(
        carpeta_logs / "ejecucion.log",
        maxBytes=5_000_000,
        backupCount=10,
        encoding="utf-8",
    )
    archivo.setFormatter(formateador)
    archivo.addFilter(filtro)

    raiz = logging.getLogger()
    raiz.setLevel(nivel)
    raiz.handlers.clear()
    raiz.addHandler(consola)
    raiz.addHandler(archivo)

    return _id_ejecucion


def obtener_registro(nombre: str) -> logging.Logger:
    """Devuelve el logger del módulo indicado. Usar `obtener_registro(__name__)`."""
    return logging.getLogger(nombre)


def obtener_id_ejecucion() -> str:
    """Devuelve el id de la corrida en curso."""
    return _id_ejecucion or "sin-id"


def carpeta_de_capturas(carpeta_logs: Path = Path("logs")) -> Path:
    """Carpeta donde se guardan las capturas de pantalla de esta corrida."""
    destino = carpeta_logs / "capturas" / obtener_id_ejecucion()
    destino.mkdir(parents=True, exist_ok=True)
    return destino
