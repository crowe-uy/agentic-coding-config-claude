"""Crea una automatización nueva a partir de la plantilla del equipo.

Copia la plantilla, la personaliza con el nombre del bot, inicializa git con
las ramas main y dev, e instala el control previo al commit.

Solo biblioteca estándar.

Uso:
    python preparar_proyecto.py --destino C:/ruta/mi-bot --nombre "Facturación de proveedores"
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

EXTENSIONES_TEXTO = {".py", ".md", ".toml", ".txt", ".yml", ".yaml", ".cfg", ".example"}

# Archivos de configuración sin extensión que también llevan marcadores a reemplazar.
ARCHIVOS_SIN_EXTENSION = {"CODEOWNERS"}

# Restos de ejecuciones locales que nunca deben viajar a un proyecto nuevo.
IGNORAR = shutil.ignore_patterns(
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".venv",
    "*.pyc",
    "logs",
    "salida",
    ".git",
)


def a_identificador(nombre: str, separador: str = "_") -> str:
    """Convierte un nombre a un identificador sin tildes ni caracteres especiales."""
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFD", nombre) if unicodedata.category(c) != "Mn"
    )
    limpio = re.sub(r"[^A-Za-z0-9]+", separador, sin_tildes).strip(separador).lower()
    return limpio or "bot"


def _git(raiz: Path, *argumentos: str) -> subprocess.CompletedProcess[str]:
    """Ejecuta git dentro del proyecto."""
    return subprocess.run(
        ["git", "-C", str(raiz), *argumentos],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def copiar_plantilla(plantilla: Path, destino: Path) -> None:
    """Copia la plantilla al destino, verificando que no pise nada."""
    if not plantilla.exists():
        raise SystemExit(f"No se encontró la plantilla en {plantilla}")
    if destino.exists() and any(destino.iterdir()):
        raise SystemExit(f"La carpeta destino no está vacía: {destino}")
    shutil.copytree(plantilla, destino, dirs_exist_ok=True, ignore=IGNORAR)


def _normalizar_referente(referente: str) -> str:
    """Acepta 'usuario', '@usuario' u 'org/equipo' y devuelve la forma que espera CODEOWNERS."""
    referente = referente.strip()
    if not referente.startswith("@"):
        referente = f"@{referente}"
    return referente


def personalizar(destino: Path, nombre: str, paquete: str, referente: str = "") -> None:
    """Renombra el paquete y reemplaza los marcadores de la plantilla.

    Si se indica `referente` (usuario u organización/equipo de GitHub), reemplaza
    también el placeholder @referente-tecnico de CODEOWNERS. Si no se indica, el
    placeholder queda para completarlo a mano antes de activar la protección de ramas.
    """
    origen = destino / "src" / "paquete_bot"
    if paquete != "paquete_bot" and origen.exists():
        origen.rename(destino / "src" / paquete)

    for archivo in destino.rglob("*"):
        si_es_texto = archivo.suffix.lower() in EXTENSIONES_TEXTO
        si_es_conocido = archivo.name in ARCHIVOS_SIN_EXTENSION
        if not archivo.is_file() or not (si_es_texto or si_es_conocido):
            continue
        texto = archivo.read_text(encoding="utf-8", errors="replace")
        nuevo = texto.replace("<NOMBRE_DEL_BOT>", nombre).replace("paquete_bot", paquete)
        nuevo = nuevo.replace("paquete-bot", paquete.replace("_", "-"))
        if referente:
            nuevo = nuevo.replace("@referente-tecnico", _normalizar_referente(referente))
        if nuevo != texto:
            archivo.write_text(nuevo, encoding="utf-8")

    plantilla_gitignore = destino / "gitignore.plantilla"
    if plantilla_gitignore.exists():
        plantilla_gitignore.rename(destino / ".gitignore")


def instalar_controles(destino: Path, scripts: Path) -> list[str]:
    """Copia el escáner de secretos e instala el hook pre-commit de git."""
    hechos: list[str] = []
    carpeta_github = destino / ".github"
    carpeta_github.mkdir(exist_ok=True)
    shutil.copy2(scripts / "escanear_secretos.py", carpeta_github / "escanear_secretos.py")
    hechos.append(".github/escanear_secretos.py")

    plantilla_hook = destino / "pre-commit.plantilla"
    hook = destino / ".git" / "hooks" / "pre-commit"
    if plantilla_hook.exists() and hook.parent.exists():
        hook.write_text(plantilla_hook.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
        hook.chmod(0o755)
        plantilla_hook.unlink()
        hechos.append(".git/hooks/pre-commit")
    return hechos


def iniciar_repositorio(destino: Path) -> list[str]:
    """Crea el repositorio git en la rama main."""
    resultado = _git(destino, "init", "-b", "main")
    if resultado.returncode != 0:
        return [f"No se pudo inicializar git: {resultado.stderr.strip()}"]
    return ["Repositorio inicializado en la rama main"]


def commit_inicial(destino: Path) -> list[str]:
    """Registra el commit inicial y crea la rama dev."""
    mensajes: list[str] = []
    identidad = _git(destino, "config", "user.email").stdout.strip()
    if not identidad:
        mensajes.append(
            "Git no tiene configurada una identidad: el commit inicial quedó pendiente. "
            "Configurá user.name y user.email y commiteá a mano."
        )
        return mensajes

    _git(destino, "add", "-A")
    commit = _git(
        destino,
        "commit",
        "-m",
        "mantenimiento: alta del proyecto desde la plantilla del equipo",
        "-m",
        "Estructura inicial, estándares de código, plantillas del ciclo y controles "
        "de seguridad previos al commit.",
    )
    if commit.returncode != 0:
        mensajes.append(
            f"El commit inicial falló: {commit.stdout.strip() or commit.stderr.strip()}"
        )
        return mensajes
    mensajes.append("Commit inicial creado en main")

    if _git(destino, "checkout", "-b", "dev").returncode == 0:
        mensajes.append("Rama dev creada y activa")
    return mensajes


def main(argumentos: list[str] | None = None) -> int:
    """Punto de entrada del preparador de proyectos."""
    analizador = argparse.ArgumentParser(description="Crea una automatización nueva.")
    analizador.add_argument("--destino", required=True, help="carpeta del proyecto nuevo")
    analizador.add_argument("--nombre", required=True, help="nombre legible del bot")
    analizador.add_argument("--paquete", help="nombre del paquete de Python (se deriva del nombre)")
    analizador.add_argument(
        "--referente",
        default="",
        help="usuario o equipo de GitHub del referente técnico, para CODEOWNERS (ej. jperez o miorg/qa)",
    )
    analizador.add_argument(
        "--plantilla",
        help="ruta de la plantilla (por defecto, la del plugin)",
    )
    opciones = analizador.parse_args(argumentos)

    aqui = Path(__file__).resolve().parent
    plantilla = Path(opciones.plantilla) if opciones.plantilla else aqui.parent / "plantilla-bot"
    destino = Path(opciones.destino).resolve()
    paquete = opciones.paquete or a_identificador(opciones.nombre)

    copiar_plantilla(plantilla, destino)
    personalizar(destino, opciones.nombre, paquete, opciones.referente)
    mensajes = iniciar_repositorio(destino)
    archivos = instalar_controles(destino, aqui)
    mensajes += commit_inicial(destino)

    print("")
    print(f"  Proyecto creado en {destino}")
    print(f"  Nombre: {opciones.nombre}   ·   Paquete: src/{paquete}")
    for mensaje in mensajes:
        print(f"   - {mensaje}")
    for archivo in archivos:
        print(f"   - Control instalado: {archivo}")
    print("")
    if opciones.referente:
        print(f"   - CODEOWNERS asignado a {_normalizar_referente(opciones.referente)}")
    else:
        print("   - Aviso: CODEOWNERS quedó con @referente-tecnico sin reemplazar.")
        print("     Completalo a mano antes de activar la protección de ramas en GitHub.")
    print("")
    print("  Próximos pasos:")
    print(r"   1. python -m venv .venv && .venv\Scripts\activate")
    print("   2. pip install -r requirements.txt -r requirements-dev.txt")
    print("   3. copy .env.example .env  y completar los valores")
    print("   4. Dejar el relevamiento en relevamiento/ y ejecutar /relevamiento")
    print("")
    return 0


if __name__ == "__main__":
    sys.exit(main())
