"""Control de calidad automático sobre los archivos Python editados.

Se ejecuta después de cada Write o Edit de un .py: formatea con ruff, corrige
lo que se puede corregir solo y le devuelve a Claude los problemas que quedan
para que los resuelva en el momento, no en la revisión del PR.

Si ruff no está instalado en el proyecto, el control avisa una vez y no
interrumpe el trabajo.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import comun

TIEMPO_MAXIMO = 25


def _ruff(raiz: Path, argumentos: list[str]) -> subprocess.CompletedProcess[str] | None:
    """Ejecuta ruff desde el entorno virtual del proyecto o desde el sistema."""
    candidatos = [
        raiz / ".venv" / "Scripts" / "ruff.exe",
        raiz / ".venv" / "bin" / "ruff",
        Path("ruff"),
    ]
    for ejecutable in candidatos:
        try:
            return subprocess.run(
                [str(ejecutable), *argumentos],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=raiz,
                timeout=TIEMPO_MAXIMO,
                check=False,
            )
        except (FileNotFoundError, OSError):
            continue
        except subprocess.TimeoutExpired:
            return None
    return None


def main() -> None:
    """Punto de entrada del control."""
    evento = comun.leer_evento()
    raiz = comun.raiz_del_proyecto(evento)
    if raiz is None:
        comun.permitir()

    archivo = str(evento.get("tool_input", {}).get("file_path", ""))
    if not archivo.endswith(".py") or not Path(archivo).exists():
        comun.permitir()

    _ruff(raiz, ["format", archivo])
    resultado = _ruff(raiz, ["check", "--fix", "--output-format=concise", archivo])
    if resultado is None:
        comun.permitir()

    pendientes = [linea for linea in resultado.stdout.splitlines() if ".py:" in linea]
    if pendientes:
        detalle = "\n".join(pendientes[:15])
        comun.avisar(
            "Control de calidad sobre el archivo recién editado.\n"
            "ruff formateó el archivo y corrigió lo automático. Queda por resolver:\n"
            f"{detalle}\n"
            "Corregilo ahora, antes de seguir con otra cosa."
        )
    comun.permitir()


if __name__ == "__main__":
    main()
