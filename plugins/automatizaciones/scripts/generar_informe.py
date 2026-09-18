"""Generador del informe de pruebas del release.

Cruza el catálogo de casos (docs/pruebas/casos.toml) con el resultado real de
pytest (JUnit XML) y con los resultados manuales cargados por el desarrollador,
y produce un index.html autocontenido para que el desarrollador y el referente
lo validen antes del pase a producción.

Solo biblioteca estándar.

Uso:
    python generar_informe.py --version 1.0.0 [--proyecto .] [--junit archivo.xml]
                              [--responsable "Nombre"] [--referente "Nombre"]

Salida: docs/pruebas/releases/<version>/index.html
"""

from __future__ import annotations

import argparse
import html
import sys
import tomllib
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

ESTADOS = {
    "exitoso": ("Exitoso", "exitoso"),
    "fallido": ("Fallido", "fallido"),
    "omitido": ("Omitido", "omitido"),
    "pendiente": ("Pendiente", "pendiente"),
}


@dataclass
class Resultado:
    """Un caso de prueba con su resultado en este release."""

    id: str
    descripcion: str
    funcionalidad: str
    casos_uso: list[str]
    tipo: str
    resultado_esperado: str
    estado: str = "pendiente"
    resultado_obtenido: str = "No ejecutado"
    fecha: str = ""
    responsable: str = ""
    evidencia: str = ""
    pasos: list[str] = field(default_factory=list)


def cargar_catalogo(ruta: Path) -> list[Resultado]:
    """Lee el catálogo de casos de prueba."""
    if not ruta.exists():
        raise SystemExit(f"No existe el catálogo de casos: {ruta}")
    datos = tomllib.loads(ruta.read_text(encoding="utf-8"))
    casos = datos.get("caso", [])
    if not casos:
        raise SystemExit(f"El catálogo {ruta} no tiene casos definidos.")
    return [
        Resultado(
            id=caso["id"],
            descripcion=caso.get("descripcion", ""),
            funcionalidad=caso.get("funcionalidad", ""),
            casos_uso=caso.get("casos_uso", []),
            tipo=caso.get("tipo", "manual"),
            resultado_esperado=caso.get("resultado_esperado", ""),
            pasos=caso.get("pasos", []),
        )
        for caso in casos
    ]


def indice_de_pruebas(ruta_catalogo: Path) -> dict[str, str]:
    """Devuelve el mapa id de caso -> identificador de la prueba automatizada."""
    datos = tomllib.loads(ruta_catalogo.read_text(encoding="utf-8"))
    return {
        caso["id"]: caso["prueba"]
        for caso in datos.get("caso", [])
        if caso.get("tipo") == "automatizada" and caso.get("prueba")
    }


def _claves_de_testcase(elemento: ET.Element) -> set[str]:
    """Identificadores posibles de un <testcase> del XML de pytest."""
    nombre = elemento.get("name", "")
    clases = elemento.get("classname", "").replace(".", "/")
    archivo = (elemento.get("file") or "").replace("\\", "/")
    claves = {f"{clases}.py::{nombre}"}
    if archivo:
        claves.add(f"{archivo}::{nombre}")
    return claves


def leer_resultados_pytest(ruta: Path) -> dict[str, tuple[str, str]]:
    """Lee el JUnit XML de pytest.

    Devuelve el mapa identificador de prueba -> (estado, detalle).
    """
    if not ruta.exists():
        return {}
    resultados: dict[str, tuple[str, str]] = {}
    for testcase in ET.parse(ruta).getroot().iter("testcase"):
        falla = testcase.find("failure")
        error = testcase.find("error")
        omitido = testcase.find("skipped")
        if falla is not None or error is not None:
            nodo = falla if falla is not None else error
            mensaje = (nodo.get("message") or "").strip() or "La prueba falló"
            estado, detalle = "fallido", mensaje.splitlines()[0][:400]
        elif omitido is not None:
            mensaje = (omitido.get("message") or "").strip() or "Prueba omitida"
            estado, detalle = "omitido", mensaje.splitlines()[0][:400]
        else:
            estado, detalle = "exitoso", "Coincide con el resultado esperado"
        for clave in _claves_de_testcase(testcase):
            resultados[clave] = (estado, detalle)
    return resultados


def leer_resultados_manuales(ruta: Path) -> dict[str, dict]:
    """Lee los resultados de las pruebas manuales cargados por el desarrollador."""
    if not ruta.exists():
        return {}
    datos = tomllib.loads(ruta.read_text(encoding="utf-8"))
    return {r["id"]: r for r in datos.get("resultado", [])}


def combinar(
    casos: list[Resultado],
    pruebas: dict[str, str],
    automatizados: dict[str, tuple[str, str]],
    manuales: dict[str, dict],
    fecha_ejecucion: str,
    responsable: str,
) -> list[Resultado]:
    """Completa cada caso del catálogo con su resultado real."""
    for caso in casos:
        if caso.tipo == "automatizada":
            identificador = pruebas.get(caso.id, "")
            encontrado = automatizados.get(identificador.replace("\\", "/"))
            if encontrado:
                caso.estado, caso.resultado_obtenido = encontrado
                caso.fecha = fecha_ejecucion
                caso.responsable = "pytest"
            else:
                caso.resultado_obtenido = (
                    f"No se encontró la prueba '{identificador}' en la ejecución de pytest"
                )
            continue

        cargado = manuales.get(caso.id)
        if cargado:
            caso.estado = cargado.get("estado", "pendiente")
            caso.resultado_obtenido = cargado.get("resultado_obtenido", "")
            caso.fecha = str(cargado.get("fecha", fecha_ejecucion))
            caso.responsable = cargado.get("responsable", responsable)
            caso.evidencia = cargado.get("evidencia", "")
        else:
            caso.resultado_obtenido = "Pendiente de ejecución manual"
    return casos


ESTILOS = """
:root {
  --tinta: #1a1a1a; --suave: #5b6570; --linea: #e2e5e9; --fondo: #ffffff;
  --panel: #f7f8fa; --ok: #1a7f4b; --okf: #e8f5ee; --mal: #c62828; --malf: #fdeaea;
  --neutro: #8a6d1f; --neutrof: #fdf6e3; --acento: #1d4ed8;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--fondo); color: var(--tinta);
  font: 15px/1.55 "Segoe UI", system-ui, -apple-system, sans-serif; }
.hoja { max-width: 1180px; margin: 0 auto; padding: 32px 28px 64px; }
h1 { font-size: 26px; margin: 0 0 4px; letter-spacing: -0.01em; }
h2 { font-size: 18px; margin: 40px 0 12px; padding-bottom: 6px;
  border-bottom: 2px solid var(--linea); }
.subtitulo { color: var(--suave); margin: 0 0 28px; }
.ficha { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 1px; background: var(--linea); border: 1px solid var(--linea); border-radius: 8px;
  overflow: hidden; margin-bottom: 28px; }
.ficha div { background: var(--panel); padding: 12px 14px; }
.ficha dt { font-size: 11px; text-transform: uppercase; letter-spacing: .06em;
  color: var(--suave); margin: 0 0 3px; }
.ficha dd { margin: 0; font-weight: 600; }
.tarjetas { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px; margin-bottom: 8px; }
.tarjeta { border: 1px solid var(--linea); border-radius: 8px; padding: 14px 16px; }
.tarjeta .n { font-size: 30px; font-weight: 700; line-height: 1.1; }
.tarjeta .r { font-size: 12px; color: var(--suave); text-transform: uppercase;
  letter-spacing: .05em; }
.tarjeta.ok .n { color: var(--ok); } .tarjeta.mal .n { color: var(--mal); }
.tarjeta.pend .n { color: var(--neutro); }
.barra { height: 10px; border-radius: 6px; background: var(--malf); overflow: hidden;
  margin: 16px 0 4px; }
.barra span { display: block; height: 100%; background: var(--ok); }
table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
th, td { text-align: left; padding: 9px 10px; border-bottom: 1px solid var(--linea);
  vertical-align: top; }
th { background: var(--panel); font-size: 11.5px; text-transform: uppercase;
  letter-spacing: .05em; color: var(--suave); position: sticky; top: 0; }
tbody tr:hover { background: #fbfcfd; }
td.id { font-family: ui-monospace, Consolas, monospace; font-weight: 600; white-space: nowrap; }
.etiqueta { display: inline-block; padding: 2px 9px; border-radius: 99px; font-size: 12px;
  font-weight: 600; white-space: nowrap; }
.exitoso { background: var(--okf); color: var(--ok); }
.fallido { background: var(--malf); color: var(--mal); }
.omitido, .pendiente { background: var(--neutrof); color: var(--neutro); }
.tipo { font-size: 12px; color: var(--suave); }
.cu { font-family: ui-monospace, Consolas, monospace; font-size: 12px; color: var(--acento); }
.aviso { border-left: 4px solid var(--mal); background: var(--malf); padding: 12px 16px;
  border-radius: 0 6px 6px 0; margin: 16px 0; }
.firmas { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; margin-top: 36px; }
.firma { border-top: 1px solid var(--tinta); padding-top: 8px; font-size: 13px;
  color: var(--suave); }
.envoltorio { overflow-x: auto; border: 1px solid var(--linea); border-radius: 8px; }
footer { margin-top: 48px; color: var(--suave); font-size: 12px; border-top: 1px solid
  var(--linea); padding-top: 14px; }
@media print {
  body { font-size: 11px; } .hoja { max-width: none; padding: 0; }
  th { position: static; } .envoltorio { border: none; }
  tbody tr { page-break-inside: avoid; }
}
"""


def _e(texto: object) -> str:
    """Escapa texto para insertarlo en el HTML."""
    return html.escape(str(texto), quote=True)


def _fila(caso: Resultado) -> str:
    """Arma la fila de la tabla para un caso."""
    etiqueta, clase = ESTADOS.get(caso.estado, ("Pendiente", "pendiente"))
    evidencia = (
        f'<a href="{_e(caso.evidencia)}">ver</a>'
        if caso.evidencia
        else '<span class="tipo">—</span>'
    )
    detalle_pasos = ""
    if caso.pasos:
        pasos = "".join(f"<li>{_e(p)}</li>" for p in caso.pasos)
        detalle_pasos = f'<ol class="tipo" style="margin:6px 0 0;padding-left:18px">{pasos}</ol>'
    return (
        "<tr>"
        f'<td class="id">{_e(caso.id)}</td>'
        f"<td>{_e(caso.fecha) or '—'}</td>"
        f"<td>{_e(caso.descripcion)}{detalle_pasos}</td>"
        f"<td>{_e(caso.funcionalidad)}<br>"
        f'<span class="cu">{_e(", ".join(caso.casos_uso))}</span></td>'
        f'<td class="tipo">{_e(caso.tipo)}<br>{_e(caso.responsable)}</td>'
        f"<td>{_e(caso.resultado_esperado)}</td>"
        f"<td>{_e(caso.resultado_obtenido)}</td>"
        f'<td><span class="etiqueta {clase}">{etiqueta}</span></td>'
        f"<td>{evidencia}</td>"
        "</tr>"
    )


def generar_html(
    casos: list[Resultado],
    proyecto: str,
    version: str,
    responsable: str,
    referente: str,
    cobertura: dict[str, list[str]],
) -> str:
    """Arma el informe completo."""
    total = len(casos)
    exitosos = sum(1 for c in casos if c.estado == "exitoso")
    fallidos = sum(1 for c in casos if c.estado == "fallido")
    pendientes = total - exitosos - fallidos
    porcentaje = round(exitosos / total * 100) if total else 0
    sin_cubrir = [cu for cu, ids in cobertura.items() if not ids]
    hoy = date.today().isoformat()

    partes: list[str] = [
        "<!doctype html>",
        '<html lang="es"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>Informe de pruebas {_e(version)} — {_e(proyecto)}</title>",
        f"<style>{ESTILOS}</style></head><body><div class=hoja>",
        f"<h1>Informe de pruebas — {_e(proyecto)}</h1>",
        f'<p class="subtitulo">Release {_e(version)} · Evidencia de validación previa '
        "al pase a producción</p>",
        '<dl class="ficha">',
        f"<div><dt>Versión</dt><dd>{_e(version)}</dd></div>",
        f"<div><dt>Fecha del informe</dt><dd>{hoy}</dd></div>",
        f"<div><dt>Responsable</dt><dd>{_e(responsable or '—')}</dd></div>",
        f"<div><dt>Referente técnico</dt><dd>{_e(referente or '—')}</dd></div>",
        "</dl>",
        "<h2>Resumen de la ejecución</h2>",
        '<div class="tarjetas">',
        f'<div class="tarjeta"><div class="n">{total}</div><div class="r">Casos</div></div>',
        f'<div class="tarjeta ok"><div class="n">{exitosos}</div>'
        '<div class="r">Exitosos</div></div>',
        f'<div class="tarjeta mal"><div class="n">{fallidos}</div>'
        '<div class="r">Fallidos</div></div>',
        f'<div class="tarjeta pend"><div class="n">{pendientes}</div>'
        '<div class="r">Sin ejecutar</div></div>',
        f'<div class="tarjeta"><div class="n">{porcentaje}%</div><div class="r">Éxito</div></div>',
        "</div>",
        f'<div class="barra"><span style="width:{porcentaje}%"></span></div>',
    ]

    if fallidos or pendientes:
        partes.append(
            '<div class="aviso"><strong>El release no está listo.</strong> '
            f"Hay {fallidos} caso(s) fallido(s) y {pendientes} sin ejecutar. "
            "Todos los casos deben quedar en estado Exitoso antes del pase a producción.</div>"
        )
    if sin_cubrir:
        partes.append(
            '<div class="aviso"><strong>Cobertura incompleta.</strong> '
            f"Sin ninguna prueba asociada: {_e(', '.join(sin_cubrir))}. "
            "Todo caso de uso del diseño debe tener al menos un caso de prueba.</div>"
        )

    partes.append("<h2>Cobertura de los casos de uso del diseño</h2>")
    partes.append('<div class="envoltorio"><table><thead><tr>')
    partes.append("<th>Caso de uso</th><th>Casos de prueba que lo verifican</th><th>Estado</th>")
    partes.append("</tr></thead><tbody>")
    por_id = {c.id: c for c in casos}
    for caso_uso, ids in cobertura.items():
        estados = [por_id[i].estado for i in ids if i in por_id]
        if not ids:
            etiqueta, clase = "Sin cubrir", "fallido"
        elif all(e == "exitoso" for e in estados):
            etiqueta, clase = "Cubierto", "exitoso"
        elif any(e == "fallido" for e in estados):
            etiqueta, clase = "Con fallas", "fallido"
        else:
            etiqueta, clase = "Incompleto", "pendiente"
        partes.append(
            f'<tr><td class="id">{_e(caso_uso)}</td>'
            f'<td class="cu">{_e(", ".join(ids)) or "—"}</td>'
            f'<td><span class="etiqueta {clase}">{etiqueta}</span></td></tr>'
        )
    partes.append("</tbody></table></div>")

    partes.append("<h2>Detalle de los casos ejecutados</h2>")
    partes.append('<div class="envoltorio"><table><thead><tr>')
    for encabezado in (
        "ID",
        "Fecha",
        "Descripción",
        "Funcionalidad probada",
        "Tipo / Ejecutor",
        "Resultado esperado",
        "Resultado obtenido",
        "Estado",
        "Evidencia",
    ):
        partes.append(f"<th>{encabezado}</th>")
    partes.append("</tr></thead><tbody>")
    partes.extend(_fila(caso) for caso in casos)
    partes.append("</tbody></table></div>")

    partes.append("<h2>Validación</h2>")
    partes.append(
        "<p>Con la firma de este informe se deja constancia de que las pruebas "
        "listadas fueron ejecutadas y de que el producto cubre los casos de uso "
        "definidos en el diseño aprobado.</p>"
    )
    partes.append('<div class="firmas">')
    partes.append(
        f'<div class="firma">Desarrollador — {_e(responsable or "")}<br>Fecha: ____________</div>'
    )
    partes.append(
        f'<div class="firma">Referente técnico — {_e(referente or "")}<br>Fecha: ____________</div>'
    )
    partes.append("</div>")
    partes.append(
        f"<footer>Generado automáticamente el {hoy} por el ciclo de implementación "
        "del equipo de automatizaciones. Fuente: docs/pruebas/casos.toml y la "
        "ejecución de pytest de este release.</footer>"
    )
    partes.append("</div></body></html>")
    return "\n".join(partes)


def calcular_cobertura(ruta_diseno: Path, casos: list[Resultado]) -> dict[str, list[str]]:
    """Mapea cada caso de uso del diseño con los casos de prueba que lo verifican."""
    import re

    cobertura: dict[str, list[str]] = {}
    if ruta_diseno.exists():
        for linea in ruta_diseno.read_text(encoding="utf-8").splitlines():
            encontrado = re.match(r"\|\s*(CU-\d+)\s*\|", linea.strip())
            if encontrado:
                cobertura[encontrado.group(1)] = []
    for caso in casos:
        for caso_uso in caso.casos_uso:
            cobertura.setdefault(caso_uso, []).append(caso.id)
    return dict(sorted(cobertura.items()))


def crear_plantilla_manuales(ruta: Path, casos: list[Resultado], hoy: str) -> None:
    """Crea el archivo de resultados manuales para que el desarrollador lo complete."""
    manuales = [c for c in casos if c.tipo == "manual"]
    if not manuales or ruta.exists():
        return
    lineas = [
        "# Resultados de las pruebas manuales de este release.",
        "# Completar 'estado' (exitoso / fallido / omitido) y 'resultado_obtenido'.",
        "# La evidencia es una ruta relativa a esta carpeta, por ejemplo evidencias/cp-015.png",
        "",
    ]
    for caso in manuales:
        lineas += [
            "[[resultado]]",
            f'id = "{caso.id}"',
            f'fecha = "{hoy}"',
            'responsable = ""',
            'estado = "pendiente"',
            'resultado_obtenido = ""',
            'evidencia = ""',
            "",
        ]
    ruta.write_text("\n".join(lineas), encoding="utf-8")
    print(f"  Creada la plantilla de resultados manuales: {ruta}")


def main(argumentos: list[str] | None = None) -> int:
    """Punto de entrada del generador."""
    analizador = argparse.ArgumentParser(description="Genera el informe de pruebas del release.")
    analizador.add_argument("--version", required=True, help="versión del release, X.Y.Z")
    analizador.add_argument("--proyecto", default=".", help="raíz del proyecto")
    analizador.add_argument("--junit", help="XML de pytest (por defecto resultados-pytest.xml)")
    analizador.add_argument("--responsable", default="", help="desarrollador responsable")
    analizador.add_argument("--referente", default="", help="referente técnico que valida")
    opciones = analizador.parse_args(argumentos)

    raiz = Path(opciones.proyecto).resolve()
    catalogo = raiz / "docs" / "pruebas" / "casos.toml"
    destino = raiz / "docs" / "pruebas" / "releases" / opciones.version
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "evidencias").mkdir(exist_ok=True)

    hoy = date.today().isoformat()
    casos = cargar_catalogo(catalogo)
    crear_plantilla_manuales(destino / "resultados-manuales.toml", casos, hoy)

    junit = Path(opciones.junit) if opciones.junit else raiz / "resultados-pytest.xml"
    if not junit.exists():
        print(f"  Aviso: no se encontró el XML de pytest en {junit}.")
        print("  Ejecutá: python -m pytest --junitxml=resultados-pytest.xml")

    casos = combinar(
        casos,
        indice_de_pruebas(catalogo),
        leer_resultados_pytest(junit),
        leer_resultados_manuales(destino / "resultados-manuales.toml"),
        hoy,
        opciones.responsable,
    )
    cobertura = calcular_cobertura(raiz / "docs" / "diseno" / "solucion.md", casos)

    informe = destino / "index.html"
    informe.write_text(
        generar_html(
            casos, raiz.name, opciones.version, opciones.responsable, opciones.referente, cobertura
        ),
        encoding="utf-8",
    )

    exitosos = sum(1 for c in casos if c.estado == "exitoso")
    fallidos = sum(1 for c in casos if c.estado == "fallido")
    print(f"  Informe generado: {informe}")
    print(f"  {exitosos}/{len(casos)} casos exitosos, {fallidos} fallidos.")
    sin_cubrir = [cu for cu, ids in cobertura.items() if not ids]
    if sin_cubrir:
        print(f"  Casos de uso sin ninguna prueba: {', '.join(sin_cubrir)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
