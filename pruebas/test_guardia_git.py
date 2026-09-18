"""Pruebas del control del flujo de ramas."""

from __future__ import annotations

import guardia_git
import pytest


def _bloquea(comando: str, rama: str) -> bool:
    try:
        guardia_git.revisar(comando, rama)
    except SystemExit as salida:
        return salida.code == 2
    return False


@pytest.mark.parametrize(
    ("comando", "rama"),
    [
        ("git commit -m prueba", "dev"),
        ("git commit -m prueba", "main"),
        ("git push origin dev", "feature/x"),
        ("git push origin main", "feature/x"),
        ("git push --force origin feature/x", "feature/x"),
        ("git commit --no-verify -m x", "feature/x"),
        ("git merge feature/descarga", "main"),
    ],
)
def test_bloquea_lo_que_rompe_el_flujo(comando: str, rama: str) -> None:
    """Las operaciones que saltean el flujo del equipo se bloquean."""
    assert _bloquea(comando, rama)


@pytest.mark.parametrize(
    ("comando", "rama"),
    [
        ("git commit -m 'funcionalidad: agrega el conector'", "feature/conector"),
        ("git push origin feature/conector", "feature/conector"),
        ("git checkout -b feature/nueva", "dev"),
        ("git status", "main"),
        ("git merge release/1.2.0", "main"),
        ("git merge hotfix/timeout", "main"),
        ("git push --force-with-lease origin feature/x", "feature/x"),
    ],
)
def test_permite_el_flujo_correcto(comando: str, rama: str) -> None:
    """El trabajo normal del equipo no se ve interrumpido."""
    assert not _bloquea(comando, rama)
