"""Servicio de cálculo de cuenta de reserva.

Este módulo expone `calcular_cuenta`, de firma estable, para ser reutilizada
por el check-out (A4) y el endpoint de consulta de cuenta.
"""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import NoEncontradoError
from app.models import Consumo, Pago, Reserva, TipoPago
from app.schemas.cuenta import CuentaDetalleConsumo, CuentaDetallePago, CuentaRead

TWO_DECIMALS = Decimal("0.01")


def _calcular_noches(entrada: date, salida: date) -> int:
    """Calcula noches de estadía: intervalo [entrada, salida).

    Si salida <= entrada, devuelve 0.
    """
    noches = (salida - entrada).days
    return max(noches, 0)


def _cuantizar(valor: Decimal | int) -> Decimal:
    """Cuantiza a 2 decimales usando redondeo bancario estándar."""
    if isinstance(valor, int):
        valor = Decimal(valor)
    return valor.quantize(TWO_DECIMALS, rounding=ROUND_HALF_UP)


def calcular_cuenta(db: Session, reserva_id: int) -> CuentaRead:
    """Calcula la cuenta completa de una reserva.

    Args:
        db: Sesión de base de datos.
        reserva_id: Identificador de la reserva.

    Returns:
        CuentaRead con:
        - total_alojamiento: noches x precio_noche_aplicado (cuantizado a 2
          decimales). Noches = (fecha_salida - fecha_entrada).days; si salida <=
          entrada => 0 noches.
        - total_consumos_vigentes: suma de consumos con anulado=False.
        - total_pagos_vigentes: suma de pagos con anulado=False; los de tipo
          REEMBOLSO se restan (son devoluciones).
        - saldo_pendiente: total_alojamiento + total_consumos_vigentes -
          total_pagos_vigentes (cuantizado).
        - detalle_consumos: TODOS los consumos de la reserva, ordenados por
          created_at, id.
        - detalle_pagos: TODOS los pagos de la reserva, ordenados por
          created_at, id.

    Raises:
        NoEncontradoError: Si la reserva no existe.
    """
    reserva = db.get(Reserva, reserva_id)
    if reserva is None:
        raise NoEncontradoError("Reserva no encontrada")

    # Noches: intervalo [entrada, salida)
    noches = _calcular_noches(reserva.fecha_entrada, reserva.fecha_salida)

    total_alojamiento = _cuantizar(reserva.precio_noche_aplicado * noches)

    # Consumos: todos, ordenados
    consumos_stmt = (
        select(Consumo)
        .where(Consumo.reserva_id == reserva_id)
        .order_by(Consumo.created_at, Consumo.id)
    )
    consumos: list[Consumo] = list(db.scalars(consumos_stmt).all())

    # Totales de consumos vigentes (anulado=False)
    total_consumos_vigentes = _cuantizar(
        sum(
            (c.precio_unitario * c.cantidad)
            for c in consumos
            if not c.anulado
        )
    )

    # Pagos: todos, ordenados
    pagos_stmt = (
        select(Pago)
        .where(Pago.reserva_id == reserva_id)
        .order_by(Pago.created_at, Pago.id)
    )
    pagos: list[Pago] = list(db.scalars(pagos_stmt).all())

    # Totales de pagos vigentes: anulado=False y tipo != REEMBOLSO
    # REEMBOLSO se resta (es devolución)
    total_pagos_vigentes = _cuantizar(
        sum(
            (p.monto if p.tipo != TipoPago.REEMBOLSO else -p.monto)
            for p in pagos
            if not p.anulado
        )
    )

    saldo_pendiente = _cuantizar(
        total_alojamiento + total_consumos_vigentes - total_pagos_vigentes
    )

    # Detalles usando los schemas dedicados con from_attributes
    detalle_consumos = [CuentaDetalleConsumo.model_validate(c) for c in consumos]
    detalle_pagos = [CuentaDetallePago.model_validate(p) for p in pagos]

    return CuentaRead(
        total_alojamiento=total_alojamiento,
        total_consumos_vigentes=total_consumos_vigentes,
        total_pagos_vigentes=total_pagos_vigentes,
        saldo_pendiente=saldo_pendiente,
        detalle_consumos=detalle_consumos,
        detalle_pagos=detalle_pagos,
    )