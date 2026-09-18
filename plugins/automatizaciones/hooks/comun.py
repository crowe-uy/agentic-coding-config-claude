"""Utilidades compartidas por los controles automáticos del plugin.

Los controles se ejecutan con el Python del sistema en cada operación de
Claude Code: tienen que ser rápidos, no escribir nada y no fallar nunca por
su cuenta.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

NIVELES_A_REVISAR = 4


def leer_evento() -> dict:
    """Lee el evento que Claude Code envía por la entrada estándar."""
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return {}


def raiz_del_proyecto(evento: dict) -> Path | None:
    """Devuelve la raíz del proyecto que el plugin debe proteger, o None si no aplica.

    Dos casos: un proyecto de automatización (tiene docs/bitacora.md) o este
    mismo repo de configuración (tiene .claude-plugin/marketplace.json, la
    raíz del marketplace). Fuera de los dos, los controles no se aplican: el
    plugin no debe estorbar en otros repositorios.
    """
    inicio = Path(evento.get("cwd") or Path.cwd())
    for carpeta in [inicio, *list(inicio.parents)[:NIVELES_A_REVISAR]]:
        if (carpeta / "docs" / "bitacora.md").exists():
            return carpeta
        if (carpeta / ".claude-plugin" / "marketplace.json").exists():
            return carpeta
    return None


def permitir() -> None:
    """Deja pasar la operación."""
    sys.exit(0)


def bloquear(titulo: str, detalle: str) -> None:
    """Bloquea la operación y le explica a Claude por qué.

    El código de salida 2 le indica a Claude Code que la herramienta no debe
    ejecutarse y que el texto de error es la explicación.
    """
    print(f"BLOQUEADO POR EL CICLO DE IMPLEMENTACIÓN: {titulo}\n\n{detalle}", file=sys.stderr)
    sys.exit(2)


def avisar(mensaje: str) -> None:
    """Deja pasar la operación, pero le comunica algo a Claude."""
    print(mensaje, file=sys.stderr)
    sys.exit(0)
