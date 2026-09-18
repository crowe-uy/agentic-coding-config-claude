"""Conector a APIs REST.

Requiere `httpx`. La importación es diferida.
"""

from __future__ import annotations

from typing import Any

from ..errores import ErrorNegocio, ErrorSistema
from ..registro import obtener_registro
from ..reintentos import con_reintentos
from .base import Conector

registro = obtener_registro(__name__)


class ConectorApi(Conector):
    """Cliente de una API REST.

    Traduce los códigos HTTP a la jerarquía del equipo: 5xx y timeouts son
    ErrorSistema (se reintentan); 4xx de validación son ErrorNegocio (no).
    """

    nombre = "api"

    def __init__(self, base_url: str, token: str, tiempo_maximo: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self._token = token
        self.tiempo_maximo = tiempo_maximo
        self._cliente: Any = None

    def conectar(self) -> None:
        """Abre el cliente HTTP."""
        try:
            import httpx
        except ImportError as error:  # pragma: no cover
            raise ErrorSistema("httpx no está instalado. Agregalo a requirements.txt.") from error

        self._cliente = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self._token}"},
            timeout=self.tiempo_maximo,
        )

    def desconectar(self) -> None:
        """Cierra el cliente HTTP."""
        if self._cliente is not None:
            self._cliente.close()

    @con_reintentos(intentos=3, espera_inicial=2.0)
    def consultar(self, recurso: str, **parametros: object) -> dict[str, Any]:
        """Consulta un recurso de la API.

        Raises:
            ErrorNegocio: si la API rechaza la solicitud por los datos enviados.
            ErrorSistema: ante fallas transitorias del servicio.
        """
        import httpx

        try:
            respuesta = self._cliente.get(recurso, params=parametros)
        except httpx.TimeoutException as error:
            raise ErrorSistema(f"Timeout consultando {recurso}") from error
        except httpx.TransportError as error:
            raise ErrorSistema(f"No se pudo alcanzar {recurso}: {error}") from error

        if respuesta.status_code >= 500:
            raise ErrorSistema(f"El servicio respondió {respuesta.status_code} en {recurso}")
        if respuesta.status_code >= 400:
            detalle = respuesta.text[:200]
            raise ErrorNegocio(
                f"La solicitud a {recurso} fue rechazada ({respuesta.status_code}): {detalle}"
            )
        return respuesta.json()
