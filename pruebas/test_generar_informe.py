"""Pruebas del generador del informe de pruebas del release."""

from __future__ import annotations

from pathlib import Path

import generar_informe

CATALOGO = """
[[caso]]
id = "CP-001"
descripcion = "Rechaza un periodo invalido"
funcionalidad = "Validaciones"
casos_uso = ["CU-001"]
tipo = "automatizada"
prueba = "pruebas/unitarias/test_modelos.py::test_periodo_invalido"
resultado_esperado = "Lanza ValueError"

[[caso]]
id = "CP-002"
descripcion = "Carga en el sistema destino"
funcionalidad = "Salida"
casos_uso = ["CU-002"]
tipo = "manual"
pasos = ["Ejecutar la corrida", "Verificar en el sistema destino"]
resultado_esperado = "El registro figura completo"
"""

JUNIT = """<?xml version="1.0"?>
<testsuites><testsuite name="pytest">
<testcase classname="pruebas.unitarias.test_modelos" name="test_periodo_invalido"
          file="pruebas/unitarias/test_modelos.py" time="0.01"/>
</testsuite></testsuites>
"""

DISENO = """
| # | Caso de uso | Resultado esperado |
|---|---|---|
| CU-001 | Validacion de entrada | Rechaza el periodo |
| CU-002 | Carga en destino | Registro creado |
| CU-003 | Portal caido | Reintenta |
"""


def _proyecto(tmp_path: Path) -> Path:
    (tmp_path / "docs" / "pruebas").mkdir(parents=True)
    (tmp_path / "docs" / "diseno").mkdir(parents=True)
    (tmp_path / "docs" / "pruebas" / "casos.toml").write_text(CATALOGO, encoding="utf-8")
    (tmp_path / "docs" / "diseno" / "solucion.md").write_text(DISENO, encoding="utf-8")
    (tmp_path / "resultados-pytest.xml").write_text(JUNIT, encoding="utf-8")
    return tmp_path


def test_genera_el_informe_con_los_resultados_reales(tmp_path: Path) -> None:
    """La prueba automatizada exitosa aparece como exitosa en el informe."""
    raiz = _proyecto(tmp_path)

    generar_informe.main(["--version", "1.0.0", "--proyecto", str(raiz), "--responsable", "Ana"])

    informe = (raiz / "docs" / "pruebas" / "releases" / "1.0.0" / "index.html").read_text(
        encoding="utf-8"
    )
    assert "CP-001" in informe
    assert 'class="etiqueta exitoso">Exitoso' in informe
    assert "Ana" in informe


def test_marca_los_casos_de_uso_sin_cubrir(tmp_path: Path) -> None:
    """Un caso de uso del diseño sin ninguna prueba se reporta como sin cubrir."""
    raiz = _proyecto(tmp_path)

    generar_informe.main(["--version", "1.0.0", "--proyecto", str(raiz)])

    informe = (raiz / "docs" / "pruebas" / "releases" / "1.0.0" / "index.html").read_text(
        encoding="utf-8"
    )
    assert "CU-003" in informe
    assert "Sin cubrir" in informe


def test_crea_la_plantilla_de_resultados_manuales(tmp_path: Path) -> None:
    """El desarrollador recibe el archivo a completar con un bloque por caso manual."""
    raiz = _proyecto(tmp_path)

    generar_informe.main(["--version", "1.0.0", "--proyecto", str(raiz)])

    plantilla = (
        raiz / "docs" / "pruebas" / "releases" / "1.0.0" / "resultados-manuales.toml"
    ).read_text(encoding="utf-8")
    assert "CP-002" in plantilla
    assert "CP-001" not in plantilla


def test_una_prueba_que_falla_aparece_como_fallida(tmp_path: Path) -> None:
    """El informe refleja el fallo real, no el resultado esperado."""
    raiz = _proyecto(tmp_path)
    (raiz / "resultados-pytest.xml").write_text(
        JUNIT.replace(
            'time="0.01"/>',
            'time="0.01"><failure message="assert 1 == 2"/></testcase>',
        ).replace("<testcase", "<testcase", 1),
        encoding="utf-8",
    )

    generar_informe.main(["--version", "1.0.0", "--proyecto", str(raiz)])

    informe = (raiz / "docs" / "pruebas" / "releases" / "1.0.0" / "index.html").read_text(
        encoding="utf-8"
    )
    assert 'class="etiqueta fallido">Fallido' in informe
    assert "El release no está listo" in informe
