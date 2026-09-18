"""Pruebas de la resolución del archivo de entorno.

Ninguno de los tres nombres se versiona (solo .env.example); esto verifica
que el orden de prioridad sea el documentado: local > dev > el genérico.
"""

from pathlib import Path

import pytest

from paquete_bot import configuracion


@pytest.mark.caso("CP-017")
def test_prefiere_env_local_sobre_los_demas(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Si existen los tres, gana .env.local."""
    # Preparar
    (tmp_path / ".env").write_text("ENTORNO=produccion\n", encoding="utf-8")
    (tmp_path / ".env.dev").write_text("ENTORNO=desarrollo-equipo\n", encoding="utf-8")
    (tmp_path / ".env.local").write_text("ENTORNO=mi-maquina\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    # Ejecutar y verificar
    assert configuracion._archivo_entorno() == tmp_path / ".env.local"


@pytest.mark.caso("CP-018")
def test_usa_env_dev_si_no_hay_local(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Sin .env.local, se usa .env.dev antes que .env."""
    # Preparar
    (tmp_path / ".env").write_text("ENTORNO=produccion\n", encoding="utf-8")
    (tmp_path / ".env.dev").write_text("ENTORNO=desarrollo-equipo\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    # Ejecutar y verificar
    assert configuracion._archivo_entorno() == tmp_path / ".env.dev"


@pytest.mark.caso("CP-019")
def test_usa_env_como_ultimo_recurso(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Sin .env.local ni .env.dev, se usa el .env genérico."""
    # Preparar
    (tmp_path / ".env").write_text("ENTORNO=produccion\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    # Ejecutar y verificar
    assert configuracion._archivo_entorno() == tmp_path / ".env"


@pytest.mark.caso("CP-020")
def test_ninguno_presente_no_falla(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Sin ningún archivo, la búsqueda no rompe: puede que las variables estén en el SO."""
    # Preparar
    monkeypatch.chdir(tmp_path)

    # Ejecutar y verificar
    assert configuracion._archivo_entorno() is None
