"""Carga y validación de la configuración del bot.

Todo se valida al arrancar, antes de abrir cualquier sistema externo: un bot
que falla al minuto 40 porque faltaba una variable de entorno está mal escrito.

Configuración (acá) es lo que cambia por entorno y es sensible: usuarios,
claves, URLs, rutas. La parametrización que maneja el usuario (Excel, CSV)
se lee aparte y se documenta en el manual.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from .errores import ErrorConfiguracion

# Orden de prioridad al buscar el archivo de entorno. Ninguno se versiona
# (solo .env.example): cada desarrollador o entorno tiene el propio.
#   .env.local  credenciales solo de tu máquina, para trabajar en Fase 2
#   .env.dev    credenciales de desarrollo compartidas por el equipo
#   .env        el que usa la ejecución real (programada o manual)
ARCHIVOS_ENTORNO = (".env.local", ".env.dev", ".env")


def _archivo_entorno() -> Path | None:
    """Devuelve el primer archivo de entorno que exista, según la prioridad."""
    for nombre in ARCHIVOS_ENTORNO:
        ruta = Path(nombre)
        if ruta.exists():
            return ruta
    return None


def obtener_variable(nombre: str, defecto: str | None = None) -> str:
    """Devuelve una variable de entorno.

    Toda variable consultada acá debe estar documentada en `.env.example`:
    el verificador del ciclo rechaza el release si falta alguna.

    Raises:
        ErrorConfiguracion: si la variable no existe y no hay valor por defecto.
    """
    valor = os.getenv(nombre, defecto)
    if valor is None or valor == "":
        raise ErrorConfiguracion(
            f"Falta la variable de entorno '{nombre}'. "
            f"Revisá tu archivo .env tomando como referencia .env.example."
        )
    return valor


def obtener_ruta(nombre: str, debe_existir: bool = True) -> Path:
    """Devuelve una ruta tomada de una variable de entorno.

    Raises:
        ErrorConfiguracion: si la variable falta o la ruta no existe.
    """
    ruta = Path(obtener_variable(nombre))
    if debe_existir and not ruta.exists():
        raise ErrorConfiguracion(f"La ruta configurada en '{nombre}' no existe: {ruta}")
    return ruta


@dataclass(frozen=True)
class Configuracion:
    """Configuración validada de la corrida.

    Agregar acá cada valor que el bot necesite, y su variable en `.env.example`.
    """

    entorno: str
    portal_url: str
    portal_usuario: str
    portal_clave: str
    carpeta_salida: Path

    def __repr__(self) -> str:
        """Representación segura: nunca expone credenciales en logs."""
        return (
            f"Configuracion(entorno={self.entorno!r}, portal_url={self.portal_url!r}, "
            f"portal_usuario={self.portal_usuario!r}, portal_clave='***', "
            f"carpeta_salida={self.carpeta_salida!r})"
        )


def cargar_configuracion() -> Configuracion:
    """Carga el archivo de entorno, valida todo y devuelve la configuración de la corrida.

    Busca `.env.local`, después `.env.dev`, después `.env` (el primero que
    exista) — ver `ARCHIVOS_ENTORNO`. Si no encuentra ninguno, sigue de todos
    modos: puede que las variables ya estén en el entorno del sistema.

    Raises:
        ErrorConfiguracion: ante cualquier variable faltante o ruta inválida.
    """
    archivo = _archivo_entorno()
    if archivo:
        load_dotenv(archivo)

    salida = Path(obtener_variable("CARPETA_SALIDA", "salida"))
    salida.mkdir(parents=True, exist_ok=True)

    return Configuracion(
        entorno=obtener_variable("ENTORNO", "desarrollo"),
        portal_url=obtener_variable("PORTAL_URL"),
        portal_usuario=obtener_variable("PORTAL_USUARIO"),
        portal_clave=obtener_variable("PORTAL_CLAVE"),
        carpeta_salida=salida,
    )
