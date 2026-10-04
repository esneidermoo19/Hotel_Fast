from enum import StrEnum


class TipoDocumento(StrEnum):
    CC = "CC"
    CE = "CE"
    PASAPORTE = "PASAPORTE"
    TI = "TI"
    OTRO = "OTRO"


class EstadoReserva(StrEnum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CHECK_IN = "CHECK_IN"
    CHECK_OUT = "CHECK_OUT"
    CANCELADA = "CANCELADA"
    NO_SHOW = "NO_SHOW"


class MetodoPago(StrEnum):
    EFECTIVO = "EFECTIVO"
    TARJETA = "TARJETA"
    TRANSFERENCIA = "TRANSFERENCIA"
    OTRO = "OTRO"


class TipoPago(StrEnum):
    ABONO = "ABONO"
    PAGO_FINAL = "PAGO_FINAL"
    REEMBOLSO = "REEMBOLSO"


class TipoTurno(StrEnum):
    MANANA = "MANANA"
    TARDE = "TARDE"
    NOCHE = "NOCHE"
    PERSONALIZADO = "PERSONALIZADO"


class EstadoLimpieza(StrEnum):
    LIMPIA = "LIMPIA"
    SUCIA = "SUCIA"


class TipoHabitacion(StrEnum):
    SIMPLE = "SIMPLE"
    DOBLE = "DOBLE"
    SUITE = "SUITE"
    PRESIDENCIAL = "PRESIDENCIAL"


class EstadoHabitacion(StrEnum):
    DISPONIBLE = "DISPONIBLE"
    OCUPADA = "OCUPADA"
    MANTENIMIENTO = "MANTENIMIENTO"