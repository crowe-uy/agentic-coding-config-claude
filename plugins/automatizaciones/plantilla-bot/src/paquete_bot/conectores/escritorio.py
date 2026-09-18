"""Conector a aplicaciones de escritorio de Windows y SAP GUI.

Requiere `pywinauto` (y SAP GUI Scripting habilitado del lado del servidor).
La importación es diferida: estas pruebas no corren en cualquier entorno.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..errores import ErrorSistema
from ..registro import obtener_registro
from .base import Conector

registro = obtener_registro(__name__)


class ConectorEscritorio(Conector):
    """Sesión sobre una aplicación de escritorio.

    En escritorio la ventana tarda y a veces roba el foco: nunca usar
    time.sleep() fijo, siempre esperar_hasta() sobre una condición de la
    ventana.
    """

    nombre = "escritorio"

    def __init__(self, ejecutable: str, titulo_ventana: str) -> None:
        self.ejecutable = ejecutable
        self.titulo_ventana = titulo_ventana
        self._aplicacion: Any = None
        self._ventana: Any = None

    def conectar(self) -> None:
        """Abre la aplicación y espera a que la ventana esté lista."""
        try:
            from pywinauto import Application
        except ImportError as error:  # pragma: no cover
            raise ErrorSistema(
                "pywinauto no está instalado. Agregalo a requirements.txt."
            ) from error

        registro.info("Abriendo la aplicación %s", self.ejecutable)
        self._aplicacion = Application(backend="uia").start(self.ejecutable)
        self._ventana = self._aplicacion.window(title_re=self.titulo_ventana)
        self._ventana.wait("visible ready", timeout=60)

    def desconectar(self) -> None:
        """Cierra la aplicación."""
        if self._aplicacion is not None:
            self._aplicacion.kill(soft=True)
        registro.info("Aplicación cerrada")

    def capturar_evidencia(self, paso: str) -> Path | None:
        """Captura la ventana activa."""
        if self._ventana is None:
            return None
        ruta = self._ruta_de_captura(paso)
        self._ventana.capture_as_image().save(str(ruta))
        return ruta
