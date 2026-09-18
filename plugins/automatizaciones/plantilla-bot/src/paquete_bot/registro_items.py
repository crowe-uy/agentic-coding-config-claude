"""Registro persistente de ítems entre etapas de un proceso modularizado.

Opcional: solo para procesos que conviene separar en etapas que corren por
separado. Ejemplo típico: una etapa toma correos y registra cada uno como
pendiente; más tarde, otra etapa (otra corrida, otro horario) lee los
pendientes, da de alta en el sistema destino y deja el resultado en el mismo
registro. Ver "Procesos en varias etapas" en docs/estandares-python.md del
plugin. Si tu bot es de una sola etapa, no importés este módulo.

Usa SQLite (`sqlite3`, biblioteca estándar) en vez de un CSV o Excel: cada
lectura y escritura es una transacción, así dos corridas que se solapan
(la etapa siguiente arranca mientras la anterior todavía escribe) no
corrompen el archivo. No pensado para alta concurrencia — para un registro
que dos o tres corridas tocan por vez, sobra.

Un `RegistroItems` es un registro. Si el bot necesita varios registros
independientes, se crean varias instancias apuntando a archivos distintos.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .modelos import EstadoItem

ESQUEMA = """
CREATE TABLE IF NOT EXISTS items (
    id TEXT PRIMARY KEY,
    estado TEXT NOT NULL DEFAULT 'pendiente',
    datos TEXT NOT NULL DEFAULT '',
    comentario TEXT NOT NULL DEFAULT '',
    creado TEXT NOT NULL,
    actualizado TEXT NOT NULL
);
"""


@dataclass(frozen=True)
class ItemRegistro:
    """Un ítem del registro, tal como está en este momento."""

    id: str
    estado: str
    datos: str
    comentario: str
    creado: str
    actualizado: str


def _ahora() -> str:
    return datetime.now().isoformat(timespec="seconds")


class RegistroItems:
    """Registro de ítems compartido entre etapas, respaldado en SQLite.

    registro = RegistroItems(raiz_ejecucion() / "estado" / "correos.db")

    # Etapa 1 (captura): un ítem por correo encontrado.
    registro.agregar(id_correo, datos=json.dumps({"asunto": asunto, "remitente": remitente}))

    # Etapa 2 (alta), en otra corrida:
    for item in registro.pendientes():
        datos = json.loads(item.datos)
        try:
            id_sistema = dar_de_alta(datos)
            registro.marcar(item.id, EstadoItem.PROCESADO, f"Alta OK, id {id_sistema}")
        except ErrorNegocio as error:
            registro.marcar(item.id, EstadoItem.EXCEPCION_NEGOCIO, str(error))
    """

    def __init__(self, ruta: Path) -> None:
        self.ruta = ruta
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        with self._conexion() as conexion:
            conexion.execute(ESQUEMA)

    @contextmanager
    def _conexion(self) -> Iterator[sqlite3.Connection]:
        conexion = sqlite3.connect(self.ruta, timeout=30)
        conexion.row_factory = sqlite3.Row
        try:
            yield conexion
            conexion.commit()
        finally:
            conexion.close()

    def agregar(self, id_item: str, datos: str = "") -> None:
        """Registra un ítem nuevo en estado pendiente.

        Idempotente: si `id_item` ya existe, no hace nada. Es lo que evita
        duplicar un ítem si la etapa que lo captura corre dos veces sobre
        el mismo período.
        """
        ahora = _ahora()
        with self._conexion() as conexion:
            conexion.execute(
                "INSERT OR IGNORE INTO items (id, estado, datos, creado, actualizado) "
                "VALUES (?, ?, ?, ?, ?)",
                (id_item, EstadoItem.PENDIENTE.value, datos, ahora, ahora),
            )

    def pendientes(self) -> list[ItemRegistro]:
        """Ítems sin procesar, del más viejo al más nuevo."""
        with self._conexion() as conexion:
            filas = conexion.execute(
                "SELECT * FROM items WHERE estado = ? ORDER BY creado",
                (EstadoItem.PENDIENTE.value,),
            ).fetchall()
        return [ItemRegistro(**dict(fila)) for fila in filas]

    def marcar(self, id_item: str, estado: EstadoItem, comentario: str = "") -> None:
        """Actualiza el estado y el comentario de un ítem ya registrado."""
        with self._conexion() as conexion:
            conexion.execute(
                "UPDATE items SET estado = ?, comentario = ?, actualizado = ? WHERE id = ?",
                (estado.value, comentario, _ahora(), id_item),
            )

    def obtener(self, id_item: str) -> ItemRegistro | None:
        """Devuelve un ítem puntual, o None si no está registrado."""
        with self._conexion() as conexion:
            fila = conexion.execute("SELECT * FROM items WHERE id = ?", (id_item,)).fetchone()
        return ItemRegistro(**dict(fila)) if fila else None

    def todos(self) -> list[ItemRegistro]:
        """Todo el registro, del más viejo al más nuevo — para reportar o depurar."""
        with self._conexion() as conexion:
            filas = conexion.execute("SELECT * FROM items ORDER BY creado").fetchall()
        return [ItemRegistro(**dict(fila)) for fila in filas]
