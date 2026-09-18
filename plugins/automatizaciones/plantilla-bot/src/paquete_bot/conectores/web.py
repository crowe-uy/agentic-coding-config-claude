"""Conector a sistemas web (Playwright).

Requiere `playwright` en requirements.txt. La importación es diferida para
que las pruebas unitarias no necesiten el navegador instalado.

Qué navegador usa (parámetro `canal`):

- `None` (por defecto): el Chromium propio de Playwright. Requiere
  `playwright install chromium` en el equipo donde corre el bot — unos 150MB,
  independiente de si ese equipo tiene Chrome, Edge o nada.
- `"msedge"`: usa el Edge que **ya viene instalado en Windows 10/11 por
  defecto**. Es la opción recomendada si el bot va a estar empaquetado en un
  .exe para un cliente que no permite instalar nada (ver docs/empaquetado.md
  del plugin): no hace falta descargar ni instalar un navegador aparte.
- `"chrome"`: usa Chrome, si está instalado en ese equipo.

Firefox no tiene equivalente: `playwright.firefox.launch()` necesita el build
propio de Playwright (`playwright install firefox`), no el Firefox público
que el cliente ya tenga instalado — no hay forma de apuntarlo a ese.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..errores import ErrorSistema
from ..registro import obtener_registro
from ..reintentos import esperar_hasta
from .base import Conector

registro = obtener_registro(__name__)


def _opciones_lanzamiento(visible: bool, canal: str | None) -> dict[str, Any]:
    """Arma los argumentos de `chromium.launch()` según canal y visibilidad."""
    opciones: dict[str, Any] = {"headless": not visible}
    if canal:
        opciones["channel"] = canal
    return opciones


class ConectorWeb(Conector):
    """Sesión de navegador sobre un portal web.

    Un método por acción del negocio (iniciar_sesion, buscar_comprobantes),
    nunca selectores sueltos en principal.py.
    """

    nombre = "web"

    def __init__(
        self,
        url: str,
        usuario: str,
        clave: str,
        visible: bool = False,
        canal: str | None = None,
    ) -> None:
        self.url = url
        self.usuario = usuario
        self.clave = clave
        self.visible = visible
        self.canal = canal
        self._navegador: Any = None
        self._pagina: Any = None
        self._playwright: Any = None

    def conectar(self) -> None:
        """Abre el navegador y carga el portal.

        Raises:
            ErrorSistema: si Playwright no está instalado, o si el canal
                pedido (ej. "msedge") no está disponible en este equipo.
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as error:  # pragma: no cover
            raise ErrorSistema(
                "Playwright no está instalado. Agregalo a requirements.txt."
            ) from error

        registro.info("Abriendo el portal %s (canal=%s)", self.url, self.canal or "chromium")
        self._playwright = sync_playwright().start()
        try:
            self._navegador = self._playwright.chromium.launch(
                **_opciones_lanzamiento(self.visible, self.canal)
            )
        except Exception as error:
            self._playwright.stop()
            self._playwright = None
            raise ErrorSistema(
                f"No se pudo abrir el navegador (canal={self.canal or 'chromium'}): {error}"
            ) from error
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
