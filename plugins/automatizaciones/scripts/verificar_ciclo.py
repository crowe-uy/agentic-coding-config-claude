"""Verificador de las aprobaciones del ciclo de implementación.

Comprueba que los artefactos obligatorios existan y estén completos antes de
avanzar de fase. Es el control automático: si esto falla, el PR no avanza.

Solo biblioteca estándar.

Uso:
    python verificar_ciclo.py --fase diseno                   Aprobación del diseño
    python verificar_ciclo.py --fase release --version 1.0.0  Validación antes de producción

Código de salida: 0 si todo está en orden, 1 si falta algo.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

SECCIONES_MANUAL = [
    "Precondiciones",
    "Postcondiciones y resultados",
    "Parametrizaciones",
    "Errores contemplados",
    "Errores conocidos",
    "Versiones del manual",
]

# Textos que solo existen mientras la plantilla no se completo.
MARCADORES_PLANTILLA = [
    "<NOMBRE_DEL_BOT>",
    "<hash>",
    "Qué problema resuelve la automatización",
    "<nombre-del-archivo.docx>",
]

RUTAS_PROHIBIDAS = [
    (r"(^|/)\.env$", "archivo .env"),
    (r"(^|/)relevamiento/(?!LEEME\.md$)", "documento de relevamiento"),
    (r"\.(pem|pfx|p12|key)$", "certificado o llave privada"),
    (r"(^|/)datos/reales/", "datos reales"),
]


@dataclass
class Control:
    """Resultado de una verificación."""

    nombre: str
    ok: bool
    detalle: str = ""

    def __str__(self) -> str:
        marca = "[OK]  " if self.ok else "[FALTA]"
        linea = f"  {marca} {self.nombre}"
        if self.detalle and (not self.ok or self.detalle.startswith("Aviso:")):
            sangria = "\n          "
            linea += sangria + self.detalle.replace("\n", sangria)
        return linea


def _leer(ruta: Path) -> str:
    """Devuelve el contenido del archivo, o cadena vacía si no existe."""
    return ruta.read_text(encoding="utf-8") if ruta.exists() else ""


def controlar_diseno(raiz: Path) -> list[Control]:
    """Controles de la aprobación del diseño: relevamiento, accesos y diseño."""
    controles: list[Control] = []

    resumen = _leer(raiz / "docs" / "relevamiento-resumen.md")
    sin_completar = [m for m in MARCADORES_PLANTILLA if m in resumen]
    controles.append(
        Control(
            "Resumen del relevamiento presente y completado",
            bool(resumen) and not sin_completar,
            "Falta docs/relevamiento-resumen.md. Ejecutá /relevamiento."
            if not resumen
            else f"El resumen sigue con texto de la plantilla sin completar: {sin_completar[0]}",
        )
    )

    preguntas = _leer(raiz / "docs" / "preguntas-abiertas.md")
    abiertas = [
        linea
        for linea in preguntas.splitlines()
        if linea.strip().startswith("| P-") and linea.rstrip().endswith("abierta |")
    ]
    controles.append(
        Control(
            "Sin preguntas abiertas al referente",
            not abiertas,
            f"Quedan {len(abiertas)} pregunta(s) en estado 'abierta'." if abiertas else "",
        )
    )

    accesos = _leer(raiz / "docs" / "accesos.md")
    sin_verificar = [
        linea
        for linea in accesos.splitlines()
        if linea.strip().startswith("| A-")
        and re.search(r"\|\s*(pendiente|solicitado)\s*\|?\s*$", linea.strip())
    ]
    controles.append(
        Control(
            "Todos los accesos verificados",
            bool(accesos) and not sin_verificar,
            f"Hay {len(sin_verificar)} acceso(s) sin verificar en docs/accesos.md."
            if sin_verificar
            else ("Falta docs/accesos.md." if not accesos else ""),
        )
    )

    diseno = _leer(raiz / "docs" / "diseno" / "solucion.md")
    es_ejemplo = "Reemplazar el ejemplo por el flujo real" in diseno
    controles.append(
        Control(
            "Diagrama de la solución en Mermaid",
            "```mermaid" in diseno and not es_ejemplo,
            "El diagrama sigue siendo el ejemplo de la plantilla. Ejecutá /diseno."
            if es_ejemplo
            else "El diseño no tiene un bloque mermaid. Ejecutá /diseno.",
        )
    )

    casos_uso = re.findall(r"^\|\s*(CU-\d+)\s*\|", diseno, flags=re.MULTILINE)
    controles.append(
        Control(
            "Matriz de casos de uso definida",
            bool(casos_uso),
            f"Se encontraron {len(casos_uso)} casos de uso."
            if casos_uso
            else "El diseño no tiene la tabla de casos de uso (filas | CU-00X |).",
        )
    )

    aprobado = re.search(r"\*\*Aprobado por\*\*\s*\|\s*([^|<]+)\|", diseno)
    nombre = aprobado.group(1).strip() if aprobado else ""
    controles.append(
        Control(
            "Diseño con aprobación registrada",
            bool(nombre) and not nombre.startswith("<"),
            "Completá 'Aprobado por' y la fecha en docs/diseno/solucion.md "
            "cuando el referente apruebe el PR."
            if not nombre or nombre.startswith("<")
            else "",
        )
    )
    return controles


def _casos_del_catalogo(raiz: Path) -> list[dict]:
    """Lee el catálogo de casos de prueba."""
    ruta = raiz / "docs" / "pruebas" / "casos.toml"
    if not ruta.exists():
        return []
    return tomllib.loads(ruta.read_text(encoding="utf-8")).get("caso", [])


def controlar_cobertura(raiz: Path) -> list[Control]:
    """Verifica que cada caso de uso del diseño tenga al menos una prueba."""
    diseno = _leer(raiz / "docs" / "diseno" / "solucion.md")
    casos_uso = set(re.findall(r"^\|\s*(CU-\d+)\s*\|", diseno, flags=re.MULTILINE))
    casos = _casos_del_catalogo(raiz)
    cubiertos = {cu for caso in casos for cu in caso.get("casos_uso", [])}
    sin_cubrir = sorted(casos_uso - cubiertos)
    huerfanos = sorted(cubiertos - casos_uso) if casos_uso else []

    return [
        Control(
            "Catálogo de casos de prueba presente",
            bool(casos),
            "Falta docs/pruebas/casos.toml con los casos de prueba." if not casos else "",
        ),
        Control(
            "Todos los casos de uso del diseño tienen prueba",
            not sin_cubrir,
            f"Sin ninguna prueba asociada: {', '.join(sin_cubrir)}." if sin_cubrir else "",
        ),
        Control(
            "El catálogo no referencia casos de uso inexistentes",
            not huerfanos,
            f"Estos casos de uso no están en el diseño: {', '.join(huerfanos)}."
            if huerfanos
            else "",
        ),
    ]


def controlar_resultados(raiz: Path, version: str) -> list[Control]:
    """Verifica que el informe del release exista y que no queden casos sin aprobar."""
    carpeta = raiz / "docs" / "pruebas" / "releases" / version
    informe = carpeta / "index.html"
    controles = [
        Control(
            f"Informe de pruebas del release {version}",
            informe.exists(),
            f"Falta {informe.relative_to(raiz)}. Ejecutá /release." if not informe.exists() else "",
        )
    ]

    casos = _casos_del_catalogo(raiz)
    manuales = {
        r["id"]: r
        for r in tomllib.loads(_leer(carpeta / "resultados-manuales.toml") or "").get(
            "resultado", []
        )
    }
    pendientes = [
        caso["id"]
        for caso in casos
        if caso.get("tipo") == "manual"
        and manuales.get(caso["id"], {}).get("estado") not in ("exitoso", "omitido")
    ]
    controles.append(
        Control(
            "Pruebas manuales ejecutadas y cargadas",
            not pendientes,
            f"Sin resultado exitoso cargado: {', '.join(pendientes)}." if pendientes else "",
        )
    )

    reporte = _leer(informe)
    fallidos = reporte.count('class="etiqueta fallido">Fallido')
    sin_ejecutar = reporte.count('class="etiqueta pendiente">Pendiente')
    omitidos = reporte.count('class="etiqueta omitido">Omitido')
    controles.append(
        Control(
            "Sin casos fallidos en el informe",
            fallidos == 0,
            f"El informe reporta {fallidos} caso(s) fallido(s)." if fallidos else "",
        )
    )
    controles.append(
        Control(
            "Sin casos sin ejecutar en el informe",
            sin_ejecutar == 0,
            f"Quedan {sin_ejecutar} caso(s) sin ejecutar." if sin_ejecutar else "",
        )
    )
    controles.append(
        Control(
            "Casos omitidos justificados",
            True,
            f"Aviso: {omitidos} caso(s) quedaron omitidos. Justificalos en la bitácora "
            "o convertilos en casos manuales."
            if omitidos
            else "",
        )
    )
    return controles


def controlar_documentacion(raiz: Path, version: str) -> list[Control]:
    """Verifica manual, bitácora y revisión del diagrama."""
    manual = _leer(raiz / "docs" / "manual-usuario.md")
    faltantes = [s for s in SECCIONES_MANUAL if f"## {s}" not in manual]
    controles = [
        Control(
            "Manual de usuario con todas las secciones exigidas",
            bool(manual) and not faltantes,
            f"Faltan secciones: {', '.join(faltantes)}." if faltantes else "",
        ),
        Control(
            f"Manual con entrada para la versión {version}",
            version in manual,
            f"La tabla 'Versiones del manual' no menciona la versión {version}."
            if version not in manual
            else "",
        ),
    ]

    bitacora = _leer(raiz / "docs" / "bitacora.md")
    controles.append(
        Control(
            f"Bitácora con la entrada del release {version}",
            version in bitacora,
            f"No hay ninguna entrada que mencione el release {version} en docs/bitacora.md."
            if version not in bitacora
            else "",
        )
    )

    diseno_revisado = re.search(
        r"(diagrama|dise\u00f1o).{0,80}(sin cambios|actualizad)",
        bitacora,
        flags=re.IGNORECASE | re.DOTALL,
    )
    controles.append(
        Control(
            "Diagrama de la solución revisado en este ciclo",
            bool(diseno_revisado),
            ""
            if diseno_revisado
            else "La bitácora debe declarar si el diagrama se actualizó o quedó sin cambios.",
        )
    )
    return controles


def controlar_variables(raiz: Path) -> list[Control]:
    """Verifica que toda variable de entorno usada esté documentada en .env.example."""
    ejemplo = _leer(raiz / ".env.example")
    documentadas = set(re.findall(r"^\s*([A-Z][A-Z0-9_]*)\s*=", ejemplo, flags=re.MULTILINE))
    usadas: set[str] = set()
    for archivo in (raiz / "src").rglob("*.py"):
        contenido = archivo.read_text(encoding="utf-8", errors="replace")
        usadas.update(
            re.findall(
                r"(?:obtener_variable|obtener_ruta|getenv|environ\.get)\(\s*[\"']([A-Z0-9_]+)[\"']",
                contenido,
            )
        )
    faltantes = sorted(usadas - documentadas)
    return [
        Control(
            "Variables de entorno documentadas en .env.example",
            not faltantes,
            f"Faltan en .env.example: {', '.join(faltantes)}." if faltantes else "",
        )
    ]


def controlar_archivos_versionados(raiz: Path) -> list[Control]:
    """Verifica que no haya archivos sensibles versionados en git."""
    resultado = subprocess.run(
        ["git", "-C", str(raiz), "ls-files"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    prohibidos = [
        ruta
        for ruta in resultado.stdout.splitlines()
        for patron, _ in RUTAS_PROHIBIDAS
        if re.search(patron, ruta)
    ]
    return [
        Control(
            "Sin archivos sensibles versionados",
            not prohibidos,
            "Estos archivos no deberían estar en el repositorio: " + ", ".join(prohibidos[:5])
            if prohibidos
            else "",
        )
    ]


def informar(titulo: str, controles: list[Control]) -> int:
    """Imprime el resultado de la verificación y devuelve el código de salida."""
    fallidos = [c for c in controles if not c.ok]
    print("")
    print("=" * 74)
    print(f"  {titulo}")
    print("=" * 74)
    for control in controles:
        print(control)
    print("")
    if fallidos:
        print(f"  RESULTADO: {len(fallidos)} de {len(controles)} controles no se cumplen.")
        print("  El ciclo no puede avanzar hasta resolverlos.")
        print("")
        return 1
    print(f"  RESULTADO: los {len(controles)} controles se cumplen. El ciclo puede avanzar.")
    print("")
    return 0


def main(argumentos: list[str] | None = None) -> int:
    """Punto de entrada del verificador."""
    analizador = argparse.ArgumentParser(description="Verifica las aprobaciones del ciclo.")
    analizador.add_argument(
        "--fase", required=True, choices=["diseno", "release"], help="aprobación a verificar"
    )
    analizador.add_argument(
        "--version", help="versión del release, obligatoria al validar antes de producción"
    )
    analizador.add_argument("--proyecto", default=".", help="raíz del proyecto")
    opciones = analizador.parse_args(argumentos)

    raiz = Path(opciones.proyecto).resolve()
    if not (raiz / "docs" / "bitacora.md").exists():
        print(f"  {raiz} no parece un proyecto de automatización: falta docs/bitacora.md.")
        return 1

    if opciones.fase == "diseno":
        controles = controlar_diseno(raiz) + controlar_archivos_versionados(raiz)
        return informar("Aprobación del diseño por el referente técnico", controles)

    if not opciones.version:
        print("  La validación del release necesita --version X.Y.Z")
        return 1

    controles = (
        controlar_cobertura(raiz)
        + controlar_resultados(raiz, opciones.version)
        + controlar_documentacion(raiz, opciones.version)
        + controlar_variables(raiz)
        + controlar_archivos_versionados(raiz)
    )
    return informar(f"Validación del release {opciones.version} antes de producción", controles)


if __name__ == "__main__":
    sys.exit(main())
