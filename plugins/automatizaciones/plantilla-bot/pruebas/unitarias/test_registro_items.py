"""Pruebas del registro persistente para procesos en varias etapas.

Cubre exactamente el patrón que describe: una etapa registra ítems
pendientes, otra corrida separada los procesa y deja el resultado.
"""

import json
from pathlib import Path

import pytest

from paquete_bot.modelos import EstadoItem
from paquete_bot.registro_items import RegistroItems


@pytest.fixture
def registro(tmp_path: Path) -> RegistroItems:
    """Registro nuevo, en un archivo temporal."""
    return RegistroItems(tmp_path / "estado" / "correos.db")


@pytest.mark.caso("CP-023")
def test_un_item_nuevo_queda_pendiente(registro: RegistroItems) -> None:
    """Al agregarlo, un ítem aparece como pendiente."""
    # Ejecutar
    registro.agregar("correo-001", datos=json.dumps({"asunto": "Alta de proveedor"}))

    # Verificar
    pendientes = registro.pendientes()
    assert len(pendientes) == 1
    assert pendientes[0].id == "correo-001"
    assert pendientes[0].estado == EstadoItem.PENDIENTE.value


@pytest.mark.caso("CP-024")
def test_agregar_el_mismo_id_dos_veces_no_duplica(registro: RegistroItems) -> None:
    """Si la etapa de captura corre dos veces sobre el mismo período, no duplica."""
    # Ejecutar
    registro.agregar("correo-001", datos="primera vez")
    registro.agregar("correo-001", datos="segunda vez, no deberia pisar nada")

    # Verificar
    assert len(registro.pendientes()) == 1
    assert registro.obtener("correo-001").datos == "primera vez"


@pytest.mark.caso("CP-025")
def test_marcar_saca_el_item_de_pendientes(registro: RegistroItems) -> None:
    """La etapa siguiente marca el resultado y el ítem deja de estar pendiente."""
    # Preparar
    registro.agregar("correo-001")

    # Ejecutar
    registro.marcar("correo-001", EstadoItem.PROCESADO, "Alta OK, id sistema 4821")

    # Verificar
    assert registro.pendientes() == []
    item = registro.obtener("correo-001")
    assert item.estado == EstadoItem.PROCESADO.value
    assert "4821" in item.comentario


@pytest.mark.caso("CP-026")
def test_un_item_inexistente_devuelve_none(registro: RegistroItems) -> None:
    """Consultar un ítem que nunca se registró no rompe, devuelve None."""
    # Ejecutar y verificar
    assert registro.obtener("no-existe") is None


@pytest.mark.caso("CP-027")
def test_el_registro_persiste_entre_instancias(tmp_path: Path) -> None:
    """Dos corridas separadas (dos instancias) ven el mismo registro en disco."""
    # Preparar: la "etapa 1" registra el ítem y termina.
    ruta = tmp_path / "estado" / "correos.db"
    RegistroItems(ruta).agregar("correo-001", datos="del período 2026-01")

    # Ejecutar: la "etapa 2" arranca en una corrida nueva, contra el mismo archivo.
    etapa_2 = RegistroItems(ruta)

    # Verificar
    pendientes = etapa_2.pendientes()
    assert len(pendientes) == 1
    assert pendientes[0].datos == "del período 2026-01"


@pytest.mark.caso("CP-028")
def test_todos_incluye_pendientes_y_procesados(registro: RegistroItems) -> None:
    """`todos()` sirve para reportar el estado completo, no solo lo pendiente."""
    # Preparar
    registro.agregar("correo-001")
    registro.agregar("correo-002")
    registro.marcar("correo-001", EstadoItem.EXCEPCION_NEGOCIO, "CUIT inválido")

    # Ejecutar
    items = registro.todos()

    # Verificar
    assert {i.id for i in items} == {"correo-001", "correo-002"}
    estados = {i.id: i.estado for i in items}
    assert estados["correo-001"] == EstadoItem.EXCEPCION_NEGOCIO.value
    assert estados["correo-002"] == EstadoItem.PENDIENTE.value
