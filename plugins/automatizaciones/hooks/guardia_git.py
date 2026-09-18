"""Control del flujo de ramas del equipo.

Se ejecuta antes de cada Bash y hace cumplir las reglas de git del ciclo:

  - no se commitea ni se pushea directo a main ni a dev;
  - no se fuerza el push sobre ramas compartidas;
  - solo release/* y hotfix/* pueden mergear a main;
  - no se saltean los controles previos al commit.
"""

from __future__ import annotations

import re
import subprocess

import comun

RAMAS_PROTEGIDAS = ("main", "master", "dev")

AYUDA_RAMAS = (
    "Flujo del equipo:\n"
    "  feature/<slug> y fix/<slug>  nacen de dev y vuelven a dev por PR\n"
    "  release/X.Y.Z                nace de dev y va a main por PR\n"
    "  hotfix/<slug>                nace de main y va a main por PR\n"
    "Creá una rama de trabajo: git checkout -b feature/<slug>"
)


def rama_actual(raiz: str) -> str:
    """Devuelve la rama activa del proyecto."""
    resultado = subprocess.run(
        ["git", "-C", raiz, "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return resultado.stdout.strip()


def revisar(comando: str, rama: str) -> None:
    """Aplica las reglas de git sobre el comando que se va a ejecutar."""
    if re.search(r"\bgit\b.*--no-verify", comando):
        comun.bloquear(
            "no se pueden saltear los controles previos al commit",
            "El control previo al commit busca credenciales y archivos sensibles.\n"
            "Si un hallazgo es un falso positivo, marcá esa línea con "
            "'# escaneo-ok: motivo' en lugar de usar --no-verify.",
        )

    if re.search(r"\bgit\s+push\b.*(\s-f\b|--force(?!-with-lease))", comando):
        comun.bloquear(
            "no se fuerza el push sobre ramas compartidas",
            "Reescribir el historial de una rama compartida rompe el trabajo del resto "
            "del equipo.\nSi necesitás deshacer algo publicado, hacelo con un commit "
            "nuevo que lo revierta.",
        )

    destino = re.search(r"\bgit\s+push\s+\S+\s+(?:HEAD:)?(\S+)", comando)
    if destino and destino.group(1).strip("'\"") in RAMAS_PROTEGIDAS:
        comun.bloquear(
            f"no se pushea directo a {destino.group(1)}",
            f"La rama {destino.group(1)} solo recibe cambios por pull request.\n" + AYUDA_RAMAS,
        )

    if rama in RAMAS_PROTEGIDAS:
        if re.search(r"\bgit\s+commit\b", comando):
            comun.bloquear(
                f"estás parado en {rama} y no se commitea ahí",
                f"La rama {rama} solo recibe cambios por pull request.\n" + AYUDA_RAMAS,
            )
        if re.search(r"\bgit\s+push\b", comando):
            comun.bloquear(
                f"estás parado en {rama} y no se pushea desde ahí",
                f"La rama {rama} solo recibe cambios por pull request.\n" + AYUDA_RAMAS,
            )

    fusion = re.search(r"\bgit\s+merge\s+(?:--\S+\s+)*(\S+)", comando)
    if fusion and rama in ("main", "master"):
        origen = fusion.group(1).strip("'\"")
        if not origen.startswith(("release/", "hotfix/")):
            comun.bloquear(
                f"no se puede mergear {origen} directamente a {rama}",
                "A producción solo llegan las ramas release/X.Y.Z y hotfix/<slug>, "
                "y siempre por pull request con el informe de pruebas adjunto.\n"
                "Si el cambio es una funcionalidad, va a dev y sale en el próximo release.",
            )


def main() -> None:
    """Punto de entrada del control."""
    evento = comun.leer_evento()
    raiz = comun.raiz_del_proyecto(evento)
    if raiz is None or evento.get("tool_name") != "Bash":
        comun.permitir()

    comando = str(evento.get("tool_input", {}).get("command", ""))
    if "git" not in comando:
        comun.permitir()

    revisar(comando, rama_actual(str(raiz)))
    comun.permitir()


if __name__ == "__main__":
    main()
