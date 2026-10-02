"""Enumeraciones compartidas del dominio.

Viven en un modulo aparte para que `catalogos.py` pueda exponerlas como
catálogos sin importar los modelos que las usan.
"""

from enum import Enum


class MetodoPago(str, Enum):
    EFECTIVO = "EFECTIVO"
    TARJETA = "TARJETA"
    TRANSFERENCIA = "TRANSFERENCIA"
    PSE = "PSE"


class TipoConsumo(str, Enum):
    MINIBAR = "MINIBAR"
    COMIDA = "COMIDA"
    BEBIDA = "BEBIDA"
    SERVICIO = "SERVICIO"
    LAVANDERIA = "LAVANDERIA"
    OTRO = "OTRO"


class EstadoReserva(str, Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CHECK_IN = "CHECK_IN"
    CHECK_OUT = "CHECK_OUT"
    CANCELADA = "CANCELADA"
    NO_SHOW = "NO_SHOW"


class TipoDocumento(str, Enum):
    CEDULA = "CEDULA"
    CEDULA_EXTRANJERA = "CEDULA_EXTRANJERA"
    PASAPORTE = "PASAPORTE"
    NIT = "NIT"
    OTRO = "OTRO"
