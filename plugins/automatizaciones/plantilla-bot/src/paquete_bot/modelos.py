"""Estructuras de datos del dominio.

Modelar los datos del negocio con dataclasses en lugar de diccionarios sueltos
hace que un campo mal escrito falle al escribirlo y no en producción.
Reemplazar estos ejemplos por los del relevamiento.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from pathlib import Path


class EstadoItem(Enum):
    """Resultado del procesamiento de un ítem."""

    PENDIENTE = "pendiente"
    PROCESADO = "procesado"
    EXCEPCION_NEGOCIO = "excepcion_negocio"
    ERROR_SISTEMA = "error_sistema"


@dataclass(frozen=True)
class Periodo:
    """Período a procesar."""

    anio: int
    mes: int

    def __post_init__(self) -> None:
        if not 1 <= self.mes <= 12:
            raise ValueError(f"Mes inválido: {self.mes}")

    def __str__(self) -> str:
        return f"{self.anio:04d}-{self.mes:02d}"


@dataclass
class Item:
    """Unidad de trabajo del bot: lo que se procesa de a uno."""

    identificador: str
    periodo: Periodo
    estado: EstadoItem = EstadoItem.PENDIENTE
    detalle: str = ""
    archivo: Path | None = None
    fecha_proceso: date | None = None


@dataclass
class ResumenEjecucion:
    """Resultado agregado de la corrida, para el log final y la notificación."""

    id_ejecucion: str
    items: list[Item] = field(default_factory=list)

    @property
    def procesados(self) -> int:
        return sum(1 for i in self.items if i.estado is EstadoItem.PROCESADO)

    @property
    def excepciones_negocio(self) -> int:
        return sum(1 for i in self.items if i.estado is EstadoItem.EXCEPCION_NEGOCIO)

    @property
    def errores_sistema(self) -> int:
        return sum(1 for i in self.items if i.estado is EstadoItem.ERROR_SISTEMA)

    def __str__(self) -> str:
        return (
            f"Total {len(self.items)} | procesados {self.procesados} | "
            f"excepciones de negocio {self.excepciones_negocio} | "
            f"errores de sistema {self.errores_sistema}"
        )
