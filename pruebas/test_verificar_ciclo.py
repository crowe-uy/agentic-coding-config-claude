"""Pruebas del verificador de las aprobaciones del ciclo."""

from __future__ import annotations

from pathlib import Path

import verificar_ciclo

DISENO_APROBADO = """
| **Aprobado por** | Referente Tecnico |
| **Fecha de aprobación** | 2026-09-17 |

```mermaid
flowchart TD
    a([Inicio]) --> b[Paso]
```

| # | Caso de uso | Resultado esperado |
|---|---|---|
| CU-001 | Camino normal | Procesado |
"""

CATALOGO = """
[[caso]]
id = "CP-001"
descripcion = "Camino normal"
funcionalidad = "Flujo"
casos_uso = ["CU-001"]
tipo = "automatizada"
prueba = "pruebas/unitarias/test_flujo.py::test_normal"
resultado_esperado = "Procesa el item"
"""


def _proyecto(tmp_path: Path, diseno: str = DISENO_APROBADO) -> Path:
    (tmp_path / "docs" / "diseno").mkdir(parents=True)
    (tmp_path / "docs" / "pruebas").mkdir(parents=True)
    (tmp_path / "docs" / "bitacora.md").write_text("# Bitácora\n", encoding="utf-8")
    (tmp_path / "docs" / "diseno" / "solucion.md").write_text(diseno, encoding="utf-8")
    (tmp_path / "docs" / "pruebas" / "casos.toml").write_text(CATALOGO, encoding="utf-8")
    return tmp_path


def test_la_aprobacion_de_diseno_falla_con_preguntas_abiertas(tmp_path: Path) -> None:
    """No se diseña sobre preguntas sin responder."""
    raiz = _proyecto(tmp_path)
    (raiz / "docs" / "preguntas-abiertas.md").write_text(
        "| P-001 | ¿Qué pasa si corre dos veces? | Bloquea | Referente | 2026-09-17 | | abierta |",
        encoding="utf-8",
    )

    controles = verificar_ciclo.controlar_diseno(raiz)

    preguntas = next(c for c in controles if "preguntas abiertas" in c.nombre)
    assert not preguntas.ok


def test_detecta_un_caso_de_uso_sin_prueba(tmp_path: Path) -> None:
    """El release se bloquea si un caso de uso del diseño no tiene prueba."""
    raiz = _proyecto(tmp_path, DISENO_APROBADO + "\n| CU-002 | Portal caído | Reintenta |\n")

    cobertura = verificar_ciclo.controlar_cobertura(raiz)

    sin_cubrir = next(c for c in cobertura if "tienen prueba" in c.nombre)
    assert not sin_cubrir.ok
    assert "CU-002" in sin_cubrir.detalle


def test_acepta_la_cobertura_completa(tmp_path: Path) -> None:
    """Con todos los casos de uso cubiertos, el control pasa."""
    raiz = _proyecto(tmp_path)

    cobertura = verificar_ciclo.controlar_cobertura(raiz)

    assert all(c.ok for c in cobertura)


def test_exige_las_secciones_del_manual(tmp_path: Path) -> None:
    """Un manual sin las secciones obligatorias no habilita el release."""
    raiz = _proyecto(tmp_path)
    (raiz / "docs" / "manual-usuario.md").write_text(
        "# Manual\n\n## Precondiciones\n\nTexto.\n", encoding="utf-8"
    )

    secciones = next(
        c for c in verificar_ciclo.controlar_documentacion(raiz, "1.0.0") if "secciones" in c.nombre
    )

    assert not secciones.ok
    assert "Errores conocidos" in secciones.detalle


def test_exige_variables_documentadas(tmp_path: Path) -> None:
    """Una variable de entorno usada y no documentada bloquea el release."""
    raiz = _proyecto(tmp_path)
    (raiz / "src").mkdir()
    (raiz / "src" / "configuracion.py").write_text(
        'clave = obtener_variable("PORTAL_CLAVE")\n', encoding="utf-8"
    )
    (raiz / ".env.example").write_text("ENTORNO=\n", encoding="utf-8")

    control = verificar_ciclo.controlar_variables(raiz)[0]

    assert not control.ok
    assert "PORTAL_CLAVE" in control.detalle


def test_rechaza_pyproject_desactualizado(tmp_path: Path) -> None:
    """Si pyproject.toml no quedó en la versión del release, se rechaza."""
    raiz = _proyecto(tmp_path)
    (raiz / "pyproject.toml").write_text(
        '[project]\nname = "bot"\nversion = "0.1.0"\n', encoding="utf-8"
    )

    control = next(
        c
        for c in verificar_ciclo.controlar_version_paquete(raiz, "1.0.0")
        if c.nombre == "pyproject.toml en la versión del release"
    )

    assert not control.ok
    assert "0.1.0" in control.detalle
    assert "1.0.0" in control.detalle


def test_acepta_pyproject_en_la_version_correcta(tmp_path: Path) -> None:
    """Con pyproject.toml y __init__.py en la versión del release, el control pasa."""
    raiz = _proyecto(tmp_path)
    (raiz / "pyproject.toml").write_text(
        '[project]\nname = "bot"\nversion = "1.0.0"\n', encoding="utf-8"
    )
    (raiz / "src" / "mi_bot").mkdir(parents=True)
    (raiz / "src" / "mi_bot" / "__init__.py").write_text(
        '__version__ = "1.0.0"\n', encoding="utf-8"
    )

    controles = verificar_ciclo.controlar_version_paquete(raiz, "1.0.0")

    assert all(c.ok for c in controles)
    assert len(controles) == 2


def test_rechaza_init_desactualizado(tmp_path: Path) -> None:
    """__init__.py con __version__ distinta a la del release bloquea el release."""
    raiz = _proyecto(tmp_path)
    (raiz / "pyproject.toml").write_text(
        '[project]\nname = "bot"\nversion = "1.0.0"\n', encoding="utf-8"
    )
    (raiz / "src" / "mi_bot").mkdir(parents=True)
    (raiz / "src" / "mi_bot" / "__init__.py").write_text(
        '__version__ = "0.9.0"\n', encoding="utf-8"
    )

    control = next(
        c
        for c in verificar_ciclo.controlar_version_paquete(raiz, "1.0.0")
        if "__init__.py" in c.nombre
    )

    assert not control.ok
    assert "0.9.0" in control.detalle
