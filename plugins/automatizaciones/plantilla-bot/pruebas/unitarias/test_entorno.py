"""Pruebas de la resolución de la carpeta base de ejecución.

Empaquetado con PyInstaller, sys.frozen queda en True y sys.executable
apunta al .exe: todo lo que el bot lee o escribe debe anclarse ahí, no al
directorio de trabajo, que el Programador de tareas de Windows no garantiza.
"""

from pathlib import Path

import pytest

from paquete_bot import entorno


@pytest.mark.caso("CP-021")
def test_usa_el_directorio_de_trabajo_si_no_esta_empaquetado(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Corriendo desde código fuente, la base es el directorio de trabajo actual."""
    # Preparar
    monkeypatch.chdir(tmp_path)
    monkeypatch.delattr("sys.frozen", raising=False)

    # Ejecutar y verificar
    assert entorno.raiz_ejecucion() == tmp_path


@pytest.mark.caso("CP-022")
def test_usa_la_carpeta_del_exe_si_esta_empaquetado(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Empaquetado, la base es la carpeta que contiene el .exe, no el cwd."""
    # Preparar
    carpeta_exe = tmp_path / "distribuible"
    carpeta_exe.mkdir()
    monkeypatch.setattr("sys.frozen", True, raising=False)
    monkeypatch.setattr("sys.executable", str(carpeta_exe / "bot.exe"), raising=False)
    monkeypatch.chdir(tmp_path)  # el cwd puede ser cualquier otro

    # Ejecutar y verificar
    assert entorno.raiz_ejecucion() == carpeta_exe
