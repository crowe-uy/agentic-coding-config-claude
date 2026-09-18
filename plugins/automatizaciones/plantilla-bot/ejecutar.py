"""Punto de entrada del bot: `python ejecutar.py`.

Agrega `src/` al path para que el paquete se importe sin instalarlo.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from paquete_bot.principal import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
