"""Control que impide escribir secretos o archivos sensibles.

Se ejecuta antes de cada Write, Edit y Bash. Bloquea:
  - escribir dentro de rutas prohibidas (.env, relevamiento/, certificados);
  - introducir credenciales en el contenido de un archivo;
  - agregar al índice de git un archivo que no debe versionarse.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import comun

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import escanear_secretos  # noqa: E402

RUTAS_ESCRITURA_PROHIBIDA = [
    (r"(^|[/\x5c])\.env$", ".env contiene credenciales y nunca se versiona"),
    (
        r"^relevamiento/(?!LEEME\.md$)",
        "la carpeta relevamiento/ guarda el documento original del cliente",
    ),
    (r"\.(pem|pfx|p12|key)$", "es un certificado o una llave privada"),
]

AGREGADO_AL_INDICE = re.compile(r"\bgit\s+add\b([^&|;]*)", re.IGNORECASE)


def _ruta_relativa(archivo: str, raiz: Path) -> str:
    """Devuelve la ruta relativa a la raiz del proyecto, con barras normales."""
    try:
        return Path(archivo).resolve().relative_to(raiz.resolve()).as_posix()
    except ValueError:
        return archivo.replace(chr(92), "/")


def revisar_escritura(evento: dict, raiz: Path) -> None:
    """Controla las herramientas Write y Edit."""
    entrada = evento.get("tool_input", {})
    archivo = str(entrada.get("file_path", ""))
    if not archivo:
        comun.permitir()

    normalizado = _ruta_relativa(archivo, raiz)
    for patron, motivo in RUTAS_ESCRITURA_PROHIBIDA:
        if re.search(patron, normalizado):
            comun.bloquear(
                f"no se puede escribir en {archivo}",
                f"Motivo: {motivo}.\n"
                "Si necesitás documentar una variable de entorno, agregala sin valor "
                "en .env.example. Si necesitás el contenido del relevamiento, resumilo "
                "en docs/relevamiento-resumen.md sin datos sensibles.",
            )

    contenido = entrada.get("content") or entrada.get("new_string") or ""
    if not contenido:
        comun.permitir()

    hallazgos = escanear_secretos.escanear_texto(normalizado, str(contenido))
    if hallazgos:
        detalle = "\n".join(str(h) for h in hallazgos[:5])
        comun.bloquear(
            "el contenido parece incluir una credencial",
            f"{detalle}\n\n"
            "Sacá el valor del código: leelo con obtener_variable('NOMBRE') y documentá "
            "la variable, sin su valor, en .env.example.\n"
            "Si es un falso positivo, agregá en esa línea el comentario "
            "'# escaneo-ok: motivo'.",
        )


def revisar_comando(evento: dict) -> None:
    """Controla los git add de la herramienta Bash."""
    comando = str(evento.get("tool_input", {}).get("command", ""))
    for agregado in AGREGADO_AL_INDICE.findall(comando):
        for ruta in agregado.split():
            if ruta.startswith("-"):
                continue
            hallazgo = escanear_secretos.revisar_ruta(ruta.strip("\"'"))
            if hallazgo:
                comun.bloquear(
                    f"no se puede agregar {ruta} al repositorio",
                    f"{hallazgo.motivo}.\nVerificá el .gitignore del proyecto antes de continuar.",
                )


def main() -> None:
    """Punto de entrada del control."""
    evento = comun.leer_evento()
    raiz = comun.raiz_del_proyecto(evento)
    if raiz is None:
        comun.permitir()
    if evento.get("tool_name") in ("Write", "Edit", "MultiEdit"):
        revisar_escritura(evento, raiz)
    elif evento.get("tool_name") == "Bash":
        revisar_comando(evento)
    comun.permitir()


if __name__ == "__main__":
    main()
