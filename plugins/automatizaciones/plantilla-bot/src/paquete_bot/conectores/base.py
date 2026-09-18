"""Base común de los conectores."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from types import TracebackType

from ..registro import carpeta_de_capturas, obtener_registro

registro = obtener_registro(__name__)


class Conector(ABC):
    """Contrato de todo conector a un sistema externo.

    Se usa siempre como gestor de contexto, para garantizar el cierre de
    sesiones, navegadores y archivos incluso ante una excepción:

        with ConectorPortal(configuracion) as portal:
            portal.iniciar_sesion()
    """

    nombre: str = "conector"

    @abstractmethod
    def conectar(self) -> None:
        """Abre la sesión o el recurso. Lanza ErrorSistema si no lo logra."""

    @abstractmethod
    def desconectar(self) -> None:
        """Cierra la sesión o el recurso. No debe lanzar excepciones."""

    def capturar_evidencia(self, paso: str) -> Path | None:  # noqa: ARG002
        """Guarda evidencia del estado actual ante un error.

        Los conectores con interfaz gráfica la sobrescriben con una captura de
        pantalla real. Devuelve la ruta del archivo generado, o None.
        """
        return None

    def __enter__(self) -> Conector:
        self.conectar()
        return self

    def __exit__(
        self,
        tipo: type[BaseException] | None,
        error: BaseException | None,
        traza: TracebackType | None,
    ) -> None:
        if error is not None:
            ruta = self.capturar_evidencia(paso="error")
            if ruta:
                registro.error("Evidencia del fallo en %s: %s", self.nombre, ruta)
        try:
            self.desconectar()
        except Exception:  # noqa: BLE001
            registro.warning("No se pudo cerrar limpiamente el conector %s", self.nombre)

    def _ruta_de_captura(self, paso: str) -> Path:
        """Ruta destino para una captura de este conector."""
        return carpeta_de_capturas() / f"{self.nombre}-{paso}.png"
