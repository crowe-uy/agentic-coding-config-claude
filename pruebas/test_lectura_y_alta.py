"""Pruebas del lector de relevamientos y del preparador de proyectos."""

from __future__ import annotations

import zipfile
from pathlib import Path

import leer_documento
import preparar_proyecto

DOCUMENTO = """<?xml version="1.0"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>
<w:p><w:r><w:t>Objetivo: descargar comprobantes</w:t></w:r></w:p>
<w:tbl><w:tr><w:tc><w:p><w:r><w:t>Sistema</w:t></w:r></w:p></w:tc>
<w:tc><w:p><w:r><w:t>Tipo</w:t></w:r></w:p></w:tc></w:tr>
<w:tr><w:tc><w:p><w:r><w:t>Portal</w:t></w:r></w:p></w:tc>
<w:tc><w:p><w:r><w:t>web</w:t></w:r></w:p></w:tc></w:tr></w:tbl>
</w:body></w:document>"""


def _docx(tmp_path: Path) -> Path:
    ruta = tmp_path / "relevamiento.docx"
    with zipfile.ZipFile(ruta, "w") as archivo:
        archivo.writestr("word/document.xml", DOCUMENTO)
    return ruta


def test_extrae_el_texto_de_un_docx(tmp_path: Path) -> None:
    """El .docx se lee sin instalar dependencias."""
    texto = leer_documento.leer_docx(_docx(tmp_path))

    assert "Objetivo: descargar comprobantes" in texto


def test_extrae_las_tablas_en_una_fila_por_linea(tmp_path: Path) -> None:
    """Las tablas del relevamiento se leen fila por fila."""
    texto = leer_documento.leer_docx(_docx(tmp_path))

    assert "Sistema | Tipo" in texto
    assert "Portal | web" in texto


def test_el_hash_identifica_el_documento(tmp_path: Path) -> None:
    """El hash da trazabilidad sin subir el documento al repositorio."""
    ruta = _docx(tmp_path)

    resumen = leer_documento.hash_del_documento(ruta)

    assert len(resumen) == 64
    assert resumen == leer_documento.hash_del_documento(ruta)


def test_deriva_el_nombre_del_paquete_sin_tildes() -> None:
    """El nombre del paquete nunca lleva tildes, eñes ni espacios."""
    assert preparar_proyecto.a_identificador("Facturación de proveedores") == (
        "facturacion_de_proveedores"
    )
    assert preparar_proyecto.a_identificador("Conciliación Ñandú") == "conciliacion_nandu"
    assert preparar_proyecto.a_identificador("Bot 2026 - v2", "-") == "bot-2026-v2"
