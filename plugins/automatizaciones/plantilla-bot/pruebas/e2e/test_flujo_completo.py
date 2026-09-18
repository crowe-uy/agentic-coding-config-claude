"""Prueba de extremo a extremo.

Requiere entorno real y sistemas disponibles. No corre en la suite normal:
se ejecuta durante el release con `python -m pytest -m e2e`.
"""

import pytest


@pytest.mark.e2e
@pytest.mark.caso("CP-014")
def test_corrida_completa_en_entorno_de_prueba() -> None:
    """La corrida completa procesa el período de prueba y deja la salida esperada."""
    pytest.skip("Pendiente: implementar cuando el entorno de prueba esté disponible.")
