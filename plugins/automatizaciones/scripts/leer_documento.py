"""Extrae el texto de un documento de relevamiento.

Un .docx es un zip con XML adentro, así que se lee con la biblioteca estándar
y no hace falta instalar nada. Para .pdf se usa pypdf o pdfplumber si están
disponibles; si no lo están, el archivo se puede leer directamente con la
herramienta Read de Claude Code.

Uso:
    python leer_documento.py relevamiento/Relevamiento.docx
    python leer_documento.py relevamiento/Relevamiento.docx --salida resumen.txt
    python leer_documento.py relevamiento/Relevamiento.docx --solo-hash
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import Path


def hash_del_documento(ruta: Path) -> str:
    """Devuelve el SHA-256 del archivo, para dejar trazabilidad sin subirlo."""
    resumen = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(65536), b""):
            resumen.update(bloque)
    return resumen.hexdigest()


def _limpiar_xml(xml: str) -> str:
    """Convierte el XML de Word en texto plano legible."""
    # Word no da significado a los saltos de linea entre etiquetas: molestan al separar celdas.
    xml = re.sub(r">\s*\n\s*<", "><", xml)
    xml = re.sub(r"<w:tab[^>]*/>", "\t", xml)
    xml = re.sub(r"<w:br[^>]*/>", "\n", xml)
    xml = re.sub(r"</w:p>\s*</w:tc>", " | ", xml)
    xml = re.sub(r"</w:tc>", " | ", xml)
    xml = re.sub(r"</w:tr>", "\n", xml)
    xml = re.sub(r"</w:p>", "\n", xml)
    texto = re.sub(r"<[^>]+>", "", xml)
    for entidad, caracter in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"')):
        texto = texto.replace(entidad, caracter)
    lineas = [linea.rstrip(" |\t") for linea in texto.splitlines()]
    return "\n".join(linea for linea in lineas if linea.strip())


def leer_docx(ruta: Path) -> str:
    """Extrae el texto de un .docx usando solo la biblioteca estándar."""
    partes: list[str] = []
    with zipfile.ZipFile(ruta) as documento:
        for nombre in ("word/document.xml", "word/footnotes.xml", "word/endnotes.xml"):
            if nombre in documento.namelist():
                partes.append(_limpiar_xml(documento.read(nombre).decode("utf-8", "replace")))
    return "\n".join(p for p in partes if p.strip())


def leer_pdf(ruta: Path) -> str:
    """Extrae el texto de un .pdf si hay alguna librería disponible."""
    try:
        from pypdf import PdfReader

        return "\n".join(pagina.extract_text() or "" for pagina in PdfReader(str(ruta)).pages)
    except ImportError:
        pass
    try:
        import pdfplumber

        with pdfplumber.open(str(ruta)) as documento:
            return "\n".join(pagina.extract_text() or "" for pagina in documento.pages)
    except ImportError:
        return (
            "[No hay ninguna librería de PDF instalada en este entorno.\n"
            " Opción 1: leer el PDF directamente con la herramienta Read de Claude Code.\n"
            " Opción 2: instalar pypdf con 'pip install pypdf' y volver a ejecutar.]"
        )


def main(argumentos: list[str] | None = None) -> int:
    """Punto de entrada del lector."""
    analizador = argparse.ArgumentParser(description="Extrae el texto de un relevamiento.")
    analizador.add_argument("archivo", help="ruta del documento")
    analizador.add_argument("--salida", help="archivo donde guardar el texto extraído")
    analizador.add_argument("--solo-hash", action="store_true", help="imprime solo el SHA-256")
    opciones = analizador.parse_args(argumentos)

    ruta = Path(opciones.archivo)
    if not ruta.exists():
        print(f"No existe el archivo {ruta}")
        return 1

    if opciones.solo_hash:
        print(hash_del_documento(ruta))
        return 0

    extension = ruta.suffix.lower()
    if extension == ".docx":
        texto = leer_docx(ruta)
    elif extension == ".pdf":
        texto = leer_pdf(ruta)
    elif extension in (".txt", ".md", ".csv"):
        texto = ruta.read_text(encoding="utf-8", errors="replace")
    else:
        print(f"Formato no soportado: {extension}. Convertí el documento a .docx o .pdf.")
        return 1

    encabezado = (
        f"# Documento: {ruta.name}\n"
        f"# SHA-256: {hash_del_documento(ruta)}\n"
        f"# Caracteres extraídos: {len(texto)}\n"
    )
    if opciones.salida:
        Path(opciones.salida).write_text(encabezado + texto, encoding="utf-8")
        print(f"Texto extraído en {opciones.salida} ({len(texto)} caracteres)")
    else:
        print(encabezado)
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
