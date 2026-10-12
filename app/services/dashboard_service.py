"""Resumen operativo y financiero del hotel para el dashboard.

Agrupa conteos sobre los modelos existentes (Reserva, Habitacion y Pago) y
sobre las cuentas calculadas por `cuenta_service.calcular_cuenta`. No crea
tablas ni campos nuevos: todo sale de lo que el dominio ya guarda.
"""

from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.tiempo import limites_utc_del_dia
from app.models import EstadoHabitacion, EstadoReserva, Habitacion, Pago, Reserva, TipoPago
from app.schemas.dashboard import DashboardRead
from app.services.cuenta_service import calcular_cuenta
from app.services.pago_service import ESTADOS_CON_PAGOS
from app.services.reserva_service import ESTADOS_QUE_BLOQUEAN

# Reservas que todavia no pasaron por el check-in.
PENDIENTES_DE_CHECK_IN: tuple[EstadoReserva, ...] = (
    EstadoReserva.PENDIENTE,
    EstadoReserva.CONFIRMADA,
)

TWO_DECIMALS = Decimal("0.01")


def _contar(db: Session, modelo: type, *condiciones: Any) -> int:
    """Cuenta filas de `modelo` que cumplen todas las `condiciones`."""
    stmt = select(func.count()).select_from(modelo).where(*condiciones)
    return int(db.scalar(stmt) or 0)


def _cuantizar(valor: Decimal | int) -> Decimal:
    """Cuantiza un importe a 2 decimales con redondeo bancario."""
    if isinstance(valor, int):
        valor = Decimal(valor)
    return valor.quantize(TWO_DECIMALS, rounding=ROUND_HALF_UP)


def _neto_pagos(
    db: Session,
    inicio: datetime | None = None,
    fin: datetime | None = None,
) -> Decimal:
    """Suma neta de pagos vigentes en el rango [inicio, fin).

    Los pagos de tipo REEMBOLSO restan (son devoluciones). Un rango `None` no
    restringe: suma todos los pagos vigentes de la historia.
    """
    consulta = select(Pago).where(Pago.anulado.is_(False))
    if inicio is not None:
        consulta = consulta.where(Pago.fecha_pago >= inicio)
    if fin is not None:
        consulta = consulta.where(Pago.fecha_pago < fin)
    total = sum(
        (pago.monto if pago.tipo != TipoPago.REEMBOLSO else -pago.monto)
        for pago in db.scalars(consulta).all()
    )
    return _cuantizar(total)


def _cuentas_con_saldo_pendiente(db: Session) -> int:
    """Cuenta las reservas con saldo pendiente mayor que cero.

    Solo se miran las cuentas que el dominio considera vigentes
    (`ESTADOS_CON_PAGOS`): canceladas y no-show quedan fuera. El calculo es el
    de `calcular_cuenta`, sin duplicar la formula.
    """
    stmt = (
        select(Reserva.id)
        .where(Reserva.estado.in_(tuple(ESTADOS_CON_PAGOS)))
        .order_by(Reserva.id)
    )
    pendientes = 0
    for reserva_id in db.scalars(stmt):
        if calcular_cuenta(db, reserva_id).saldo_pendiente > 0:
            pendientes += 1
    return pendientes


def resumen_dashboard(db: Session, hoy: date) -> DashboardRead:
    """Resumen operativo del hotel para `hoy` (fecha en America/Bogota).

    - reservas_activas: en PENDIENTE, CONFIRMADA o CHECK_IN; es decir, las que
      aun cuentan para la ocupacion (`ESTADOS_QUE_BLOQUEAN`).
    - reservas_pendientes_check_in: en PENDIENTE o CONFIRMADA.
    - huespedes_alojados: suma de `numero_huespedes` de las reservas en
      CHECK_IN (personas alojadas, no reservas).
    - check_outs_del_dia: `check_out_real` dentro del dia en Bogota, calculado
      con `limites_utc_del_dia` para no confundir la fecha UTC con la local.
    - habitaciones_*: conteo por `EstadoHabitacion`.
    - cuentas_con_saldo_pendiente: reservas con cuenta vigente y saldo > 0.
    - tasa_ocupacion: ocupadas sobre operativas (disponibles + ocupadas).
    - ingresos_del_dia: pagos vigentes de hoy (reembolsos restados).
    - revpar: ingresos_del_dia entre habitaciones operativas.
    - balance_caja: pagos vigentes acumulados menos reembolsos acumulados.
    """
    inicio_dia_utc, fin_dia_utc = limites_utc_del_dia(hoy)

    reservas_activas = _contar(db, Reserva, Reserva.estado.in_(ESTADOS_QUE_BLOQUEAN))
    pendientes_check_in = _contar(
        db, Reserva, Reserva.estado.in_(PENDIENTES_DE_CHECK_IN)
    )
    alojados = int(
        db.scalar(
            select(func.coalesce(func.sum(Reserva.numero_huespedes), 0)).where(
                Reserva.estado == EstadoReserva.CHECK_IN
            )
        )
        or 0
    )
    check_outs_del_dia = _contar(
        db,
        Reserva,
        Reserva.estado == EstadoReserva.CHECK_OUT,
        Reserva.check_out_real.is_not(None),
        Reserva.check_out_real >= inicio_dia_utc,
        Reserva.check_out_real < fin_dia_utc,
    )
    disponibles = _contar(
        db, Habitacion, Habitacion.estado == EstadoHabitacion.DISPONIBLE
    )
    ocupadas = _contar(db, Habitacion, Habitacion.estado == EstadoHabitacion.OCUPADA)
    mantenimiento = _contar(
        db, Habitacion, Habitacion.estado == EstadoHabitacion.MANTENIMIENTO
    )

    operativas = disponibles + ocupadas
    tasa_ocupacion = (
        round(ocupadas / operativas * 100, 1) if operativas else 0.0
    )

    ingresos_del_dia = _neto_pagos(db, inicio_dia_utc, fin_dia_utc)
    revpar = _cuantizar(ingresos_del_dia / operativas) if operativas else Decimal("0")
    balance_caja = _neto_pagos(db)

    return DashboardRead(
        reservas_activas=reservas_activas,
        reservas_pendientes_check_in=pendientes_check_in,
        huespedes_alojados=alojados,
        check_outs_del_dia=check_outs_del_dia,
        habitaciones_disponibles=disponibles,
        habitaciones_ocupadas=ocupadas,
        habitaciones_en_mantenimiento=mantenimiento,
        cuentas_con_saldo_pendiente=_cuentas_con_saldo_pendiente(db),
        tasa_ocupacion=tasa_ocupacion,
        ingresos_del_dia=ingresos_del_dia,
        revpar=revpar,
        balance_caja=balance_caja,
    )
