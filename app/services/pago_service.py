
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import ConflictoError, NoEncontradoError, ReglaNegocioError
from app.core.pagination import paginar_consulta
from app.core.tiempo import ahora_utc
from app.models import EstadoReserva, Pago, Reserva
from app.schemas.pago import PagoAnular, PagoCreate

ESTADOS_CON_PAGOS = {
    EstadoReserva.PENDIENTE,
    EstadoReserva.CONFIRMADA,
    EstadoReserva.CHECK_IN,
    EstadoReserva.CHECK_OUT,
}


class PagoYaAnuladoError(ConflictoError):
    codigo = "PAGO_YA_ANULADO"

    def __init__(self) -> None:
        super().__init__("El pago ya fue anulado")


class ReservaNoPermitePagosError(ReglaNegocioError):
    codigo = "RESERVA_NO_PERMITE_PAGOS"

    def __init__(self, estado: EstadoReserva) -> None:
        super().__init__(
            f"No se pueden registrar pagos en reserva con estado {estado.value}"
        )


def _obtener_reserva_o_404(db: Session, reserva_id: int) -> Reserva:
    reserva = db.get(Reserva, reserva_id)
    if reserva is None:
        raise NoEncontradoError("Reserva no encontrada")
    return reserva


def _obtener_pago_o_404(db: Session, pago_id: int, reserva_id: int) -> Pago:
    pago = db.get(Pago, pago_id)
    if pago is None or pago.reserva_id != reserva_id:
        raise NoEncontradoError("Pago no encontrado")
    return pago


def listar_pagos(
    db: Session,
    reserva_id: int,
    *,
    pagina: int = 1,
    tamano: int = 20,
    solo_vigentes: bool = False,
) -> tuple[list[Pago], int]:
    _obtener_reserva_o_404(db, reserva_id)

    consulta = select(Pago).where(Pago.reserva_id == reserva_id)
    if solo_vigentes:
        consulta = consulta.where(Pago.anulado.is_(False))

    total = db.scalar(
        select(func.count()).select_from(consulta.subquery())
    )
    items = list(
        db.scalars(
            paginar_consulta(
                consulta.order_by(Pago.created_at.desc(), Pago.id.desc()),
                pagina=pagina,
                tamano=tamano,
            )
        ).all()
    )
    return items, total or 0


def crear_pago(
    db: Session,
    reserva_id: int,
    datos: PagoCreate,
    usuario_id: int,
) -> Pago:
    reserva = _obtener_reserva_o_404(db, reserva_id)

    if reserva.estado not in ESTADOS_CON_PAGOS:
        raise ReservaNoPermitePagosError(reserva.estado)

    fecha_pago = datos.fecha_pago or ahora_utc()

    pago = Pago(
        reserva_id=reserva_id,
        monto=datos.monto,
        metodo=datos.metodo,
        tipo=datos.tipo,
        referencia=datos.referencia,
        fecha_pago=fecha_pago,
        registrado_por=usuario_id,
    )
    db.add(pago)
    db.commit()
    db.refresh(pago)
    return pago


def anular_pago(
    db: Session,
    reserva_id: int,
    pago_id: int,
    datos: PagoAnular,
    usuario_id: int,
) -> Pago:
    pago = _obtener_pago_o_404(db, pago_id, reserva_id)

    if pago.anulado:
        raise PagoYaAnuladoError()

    pago.anulado = True
    pago.anulado_por = usuario_id
    pago.anulado_en = ahora_utc()
    pago.motivo_anulacion = datos.motivo_anulacion
    db.commit()
    db.refresh(pago)
    return pago