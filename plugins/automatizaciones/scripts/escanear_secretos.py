"""Escáner de secretos e información sensible.

Solo biblioteca estándar: se ejecuta con el Python del sistema, tanto desde el
hook de Claude Code como desde el hook pre-commit de git.

Modos de uso:
    escanear_secretos.py --staged                  Diff en el índice de git
    escanear_secretos.py --rango dev..HEAD         Diff entre dos referencias
    escanear_secretos.py --archivos a.py b.md      Archivos sueltos
    escanear_secretos.py --texto-stdin --nombre x  Texto por entrada estándar

Código de salida: 0 si está limpio, 1 si encontró algo.

Para marcar un falso positivo, agregar en la misma línea el comentario:
    # escaneo-ok: motivo
"""

from __future__ import annotations

import argparse
import math
import re
import subprocess
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

# --- Rutas que nunca deben versionarse -------------------------------------

RUTAS_PROHIBIDAS: list[tuple[str, str]] = [
    (r"(^|/)\.env$", "archivo .env con credenciales"),
    (r"(^|/)\.env\.(?!example$)[A-Za-z0-9_.-]+$", "variante de .env con credenciales"),
    (r"^(\./)?relevamiento/(?!LEEME\.md$)", "documento de relevamiento"),
    (r"\.(pem|pfx|p12|key|jks|keystore)$", "certificado o llave privada"),
    (r"(^|/)credenciales", "archivo de credenciales"),
    (r"(^|/)datos/reales/", "datos reales de producción"),
    (r"\.(docx?|pdf)$", "documento ofimático: ¿es el relevamiento?"),
]

# --- Patrones de secreto en el contenido -----------------------------------

PATRONES: list[tuple[str, str]] = [
    (
        r"(?i)[A-Za-z0-9_.-]*(password|passwd|pwd|contrasena|contraseña|clave|"
        r"secret|token|api[_-]?key|apikey|access[_-]?key|authorization)[A-Za-z0-9_.-]*"
        r"\s*[:=]\s*[\"']?([^\s\"';,]{6,})",
        "posible credencial asignada en el código",
    ),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "llave privada embebida"),
    (r"\bAKIA[0-9A-Z]{16}\b", "clave de acceso de AWS"),
    (r"\bgh[pousr]_[A-Za-z0-9]{30,}\b", "token de GitHub"),
    (r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b", "token de Slack"),
    (r"(?i)\bbearer\s+[A-Za-z0-9._\-]{20,}", "token bearer embebido"),
]

# Valores que parecen secretos pero no lo son.
VALOR_INOFENSIVO = re.compile(
    r"^(\s*|[<\[{].*|.*[}>\]]\s*|\**|x{3,}|\.{3,}|-+|"
    r"(?i:none|null|true|false|todo|pendiente|ejemplo|example|dummy|test|prueba|"
    r"tu-clave|su-clave|valor|placeholder|cambiar|completar))$"
)

# Si el valor es una llamada o una interpolación, no es un secreto literal.
VALOR_DINAMICO = re.compile(
    r"(getenv|environ|obtener_variable|obtener_ruta|config\.|self\.|\$\{|%\w+%|\(|\{)"
)

EXENCION = re.compile(r"#\s*escaneo-ok\s*:", re.IGNORECASE)

# Archivos donde los ejemplos de variables son esperables.
ARCHIVOS_EXENTOS = re.compile(
    r"(\.env\.example$|\.example$|escanear_secretos\.py$|(^|/)docs/seguridad\.md$)"
)

LARGO_MINIMO_ENTROPIA = 32
ENTROPIA_MINIMA = 4.6


@dataclass
class Hallazgo:
    """Un problema detectado."""

    archivo: str
    linea: int
    motivo: str
    fragmento: str

    def __str__(self) -> str:
        ubicacion = f"{self.archivo}:{self.linea}" if self.linea else self.archivo
        return f"  {ubicacion}\n      {self.motivo}\n      {self.fragmento}"


def entropia(texto: str) -> float:
    """Entropía de Shannon del texto, en bits por carácter."""
    if not texto:
        return 0.0
    total = len(texto)
    resultado = 0.0
    for caracter in dict.fromkeys(texto):
        proporcion = texto.count(caracter) / total
        resultado -= proporcion * math.log2(proporcion)
    return resultado


def enmascarar(fragmento: str, limite: int = 110) -> str:
    """Recorta y oculta el posible secreto para no imprimirlo entero."""
    fragmento = fragmento.strip()
    if len(fragmento) > limite:
        fragmento = fragmento[:limite] + "..."
    return re.sub(r"([:=]\s*[\"']?)([^\s\"']{4})[^\s\"']+", r"\1\2***", fragmento)


def revisar_ruta(ruta: str) -> Hallazgo | None:
    """Verifica si la ruta corresponde a un archivo que no debe versionarse."""
    normalizada = str(PurePosixPath(ruta.replace("\\", "/")))
    for patron, motivo in RUTAS_PROHIBIDAS:
        if re.search(patron, normalizada):
            return Hallazgo(ruta, 0, f"Archivo que no debe subirse: {motivo}", normalizada)
    return None


def revisar_linea(archivo: str, numero: int, linea: str) -> Hallazgo | None:
    """Busca patrones de secreto en una línea."""
    if EXENCION.search(linea) or ARCHIVOS_EXENTOS.search(archivo.replace("\\", "/")):
        return None

    for patron, motivo in PATRONES:
        coincidencia = re.search(patron, linea)
        if not coincidencia:
            continue
        valor = coincidencia.group(coincidencia.lastindex or 0)
        if VALOR_INOFENSIVO.match(valor) or VALOR_DINAMICO.search(valor):
            continue
        return Hallazgo(archivo, numero, motivo, enmascarar(linea))

    patron_largo = rf"[A-Za-z0-9+/=_-]{{{LARGO_MINIMO_ENTROPIA},}}"
    for candidato in re.findall(patron_largo, linea):
        if entropia(candidato) >= ENTROPIA_MINIMA and not VALOR_INOFENSIVO.match(candidato):
            return Hallazgo(
                archivo,
                numero,
                "cadena larga y aleatoria: ¿es un token o una clave?",
                enmascarar(linea),
            )
    return None


def _git(*argumentos: str) -> str:
    """Ejecuta un comando de git y devuelve su salida."""
    resultado = subprocess.run(
        ["git", *argumentos],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if resultado.returncode != 0:
        print(f"No se pudo ejecutar git: {resultado.stderr.strip()}")
        return ""
    return resultado.stdout


def lineas_del_diff(diff: str) -> Iterator[tuple[str, int, str]]:
    """Recorre un diff unificado: entrega archivo, número de línea y texto agregado."""
    archivo = ""
    numero = 0
    for linea in diff.splitlines():
        if linea.startswith("+++ b/"):
            archivo = linea[6:]
            numero = 0
        elif linea.startswith("@@"):
            encabezado = re.search(r"\+(\d+)", linea)
            numero = int(encabezado.group(1)) if encabezado else 0
        elif linea.startswith("+") and not linea.startswith("+++"):
            yield archivo, numero, linea[1:]
            numero += 1
        elif not linea.startswith("-"):
            numero += 1


def escanear_diff(diff: str, archivos: list[str]) -> list[Hallazgo]:
    """Escanea las rutas y las líneas agregadas de un diff."""
    hallazgos: list[Hallazgo] = []
    for ruta in archivos:
        hallazgo = revisar_ruta(ruta)
        if hallazgo:
            hallazgos.append(hallazgo)
    for archivo, numero, contenido in lineas_del_diff(diff):
        hallazgo = revisar_linea(archivo, numero, contenido)
        if hallazgo:
            hallazgos.append(hallazgo)
    return hallazgos


def escanear_texto(nombre: str, texto: str) -> list[Hallazgo]:
    """Escanea un texto completo, línea por línea."""
    hallazgos: list[Hallazgo] = []
    hallazgo = revisar_ruta(nombre)
    if hallazgo:
        hallazgos.append(hallazgo)
    for numero, linea in enumerate(texto.splitlines(), start=1):
        hallazgo = revisar_linea(nombre, numero, linea)
        if hallazgo:
            hallazgos.append(hallazgo)
    return hallazgos


def informar(hallazgos: list[Hallazgo]) -> int:
    """Imprime los hallazgos y devuelve el código de salida."""
    if not hallazgos:
        return 0
    print("")
    print("=" * 74)
    print(f"  ESCANEO DE SECRETOS: {len(hallazgos)} hallazgo(s). La operación se bloquea.")
    print("=" * 74)
    for hallazgo in hallazgos:
        print(hallazgo)
    print("")
    print("  Qué hacer:")
    print("   - Si es una credencial: sacala del código, ponela en .env y")
    print("     documentá la variable, sin valor, en .env.example.")
    print("   - Si es un archivo sensible: quitalo del índice con")
    print("     git restore --staged <archivo> y revisá el .gitignore.")
    print("   - Si es un falso positivo: agregá '# escaneo-ok: motivo' en esa línea.")
    print("   - Si ya se subió una credencial real: ROTALA AHORA y avisá al referente.")
    print("")
    return 1


def main(argumentos: list[str] | None = None) -> int:
    """Punto de entrada del escáner."""
    analizador = argparse.ArgumentParser(description="Escáner de secretos del equipo.")
    grupo = analizador.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--staged", action="store_true", help="escanea el índice de git")
    grupo.add_argument("--rango", help="escanea un rango de commits, por ejemplo dev..HEAD")
    grupo.add_argument("--archivos", nargs="+", help="escanea archivos sueltos")
    grupo.add_argument("--texto-stdin", action="store_true", help="escanea la entrada estándar")
    analizador.add_argument("--nombre", default="(texto)", help="nombre del archivo escaneado")
    opciones = analizador.parse_args(argumentos)

    if opciones.staged:
        lista = [r for r in _git("diff", "--cached", "--name-only").splitlines() if r]
        return informar(escanear_diff(_git("diff", "--cached", "-U0"), lista))

    if opciones.rango:
        lista = [r for r in _git("diff", "--name-only", opciones.rango).splitlines() if r]
        return informar(escanear_diff(_git("diff", "-U0", opciones.rango), lista))

    if opciones.archivos:
        hallazgos: list[Hallazgo] = []
        for ruta in opciones.archivos:
            prohibida = revisar_ruta(ruta)
            if prohibida:
                hallazgos.append(prohibida)
            try:
                texto = Path(ruta).read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            hallazgos.extend(
                h
                for numero, linea in enumerate(texto.splitlines(), start=1)
                if (h := revisar_linea(ruta, numero, linea))
            )
        return informar(hallazgos)

    return informar(escanear_texto(opciones.nombre, sys.stdin.read()))


if __name__ == "__main__":
    sys.exit(main())
