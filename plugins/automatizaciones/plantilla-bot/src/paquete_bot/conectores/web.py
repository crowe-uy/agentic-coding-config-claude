"""Conector a sistemas web (Playwright).

Requiere `playwright` en requirements.txt y `playwright install chromium`.
La importación es diferida para que las pruebas unitarias no necesiten el
navegador instalado.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..errores import ErrorSistema
from ..registro import obtener_registro
from ..reintentos import esperar_hasta
from .base import Conector

registro = obtener_registro(__name__)


class ConectorWeb(Conector):
    """Sesión de navegador sobre un portal web.

    Un método por acción del negocio (iniciar_sesion, buscar_comprobantes),
    nunca selectores sueltos en principal.py.
    """

    nombre = "web"

    def __init__(self, url: str, usuario: str, clave: str, visible: bool = False) -> None:
        self.url = url
        self.usuario = usuario
        self.clave = clave
        self.visible = visible
        self._navegador: Any = None
        self._pagina: Any = None
        self._playwright: Any = None

    def conectar(self) -> None:
        """Abre el navegador y carga el portal."""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as error:  # pragma: no cover
            raise ErrorSistema(
                "Playwright no está instalado. Agregalo a requirements.txt y "
                "ejecutá: playwright install chromium"
            ) from error

        registro.info("Abriendo el portal %s", self.url)
        self._playwright = sync_playwright().start()
        self._navegador = self._playwright.chromium.launch(headless=not self.visible)
        self._pagina = self._navegador.new_page()
        self._pagina.goto(self.url, timeout=60_000)

    def desconectar(self) -> None:
        """Cierra el navegador."""
        if self._navegador is not None:
            self._navegador.close()
        if self._playwright is not None:
            self._playwright.stop()
        registro.info("Portal cerrado")

    def capturar_evidencia(self, paso: str) -> Path | None:
        """Captura la pantalla del navegador."""
        if self._pagina is None:
            return None
        ruta = self._ruta_de_captura(paso)
        self._pagina.screenshot(path=str(ruta), full_page=True)
        return ruta

    def iniciar_sesion(self) -> None:
        """Autentica en el portal.

        Raises:
            ErrorSistema: si el portal no responde o el login no se completa.
        """
        # TODO: reemplazar los selectores por los reales del portal.
        self._pagina.fill("#usuario", self.usuario)
        self._pagina.fill("#clave", self.clave)
        self._pagina.click("#ingresar")
        esperar_hasta(
            lambda: self._pagina.is_visible("#menu-principal"),
            tiempo_maximo=30,
            descripcion="el menú principal del portal",
        )
        registro.info("Sesión iniciada como %s", self.usuario)
