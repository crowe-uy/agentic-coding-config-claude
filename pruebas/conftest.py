"""Configuración de las pruebas de los scripts del plugin."""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "plugins" / "automatizaciones" / "scripts"))
sys.path.insert(0, str(RAIZ / "plugins" / "automatizaciones" / "hooks"))
