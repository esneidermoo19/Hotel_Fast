"""Resumen operativo del hotel para el dashboard.

Agrupa conteos sobre los modelos existentes (Reserva y Habitacion) y sobre las
cuentas calculadas por `cuenta_service.calcular_cuenta`. No crea tablas ni
campos nuevos: todo sale de lo que el dominio ya guarda.
"""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.tiempo import limites_utc_del_dia
from app.models import EstadoHabitacion, EstadoReserva, Habitacion, Reserva
from app.schemas.dashboard import DashboardRead
from app.services.cuenta_service import calcular_cuenta
from app.services.pago_service import ESTADOS_CON_PAGOS
from app.services.reserva_service import ESTADOS_QUE_BLOQUEAN

# Reservas que todavia no pasaron por el check-in.
PENDIENTES_DE_CHECK_IN: tuple[EstadoReserva, ...] = (
    EstadoReserva.PENDIENTE,
    EstadoReserva.CONFIRMADA,
)


def _contar(db: Session, modelo: type, *condiciones: object) -> int:
    """Cuenta filas de `modelo` que cumplen todas las `condiciones`."""
    stmt = select(func.count()).select_from(modelo).where(*condiciones)
    return int(db.scalar(stmt) or 0)


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

    return DashboardRead(
        reservas_activas=reservas_activas,
        reservas_pendientes_check_in=pendientes_check_in,
        huespedes_alojados=alojados,
        check_outs_del_dia=check_outs_del_dia,
        habitaciones_disponibles=disponibles,
        habitaciones_ocupadas=ocupadas,
        habitaciones_en_mantenimiento=mantenimiento,
        cuentas_con_saldo_pendiente=_cuentas_con_saldo_pendiente(db),
    )
