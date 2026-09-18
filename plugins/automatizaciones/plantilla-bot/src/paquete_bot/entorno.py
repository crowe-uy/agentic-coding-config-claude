"""Resuelve la carpeta base de la ejecución: código fuente vs. empaquetado.

Corriendo desde código fuente (`python ejecutar.py`), la base es el directorio
de trabajo actual — de donde se invocó el comando.

Empaquetado con PyInstaller (ver docs/empaquetado.md del plugin), el .exe
puede arrancar con cualquier directorio de trabajo: el Programador de tareas
de Windows no garantiza cuál. Ahí la base pasa a ser la carpeta donde está
el .exe, para que `.env*`, `logs/`, `salida/`, `estado/`, `parametros/` y
`recursos/` se resuelvan siempre igual sin importar quién ni cómo lo lanzó.

Todo lo que el bot lee o escribe con una ruta relativa debe anclarse acá.
"""

from __future__ import annotations

import sys
from pathlib import Path


def raiz_ejecucion() -> Path:
    """Carpeta base para resolver rutas relativas del bot.

    - Empaquetado (PyInstaller): la carpeta donde está el .exe.
    - Desde código fuente: el directorio de trabajo actual.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path.cwd()
