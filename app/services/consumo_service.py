
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import ConflictoError, NoEncontradoError, ReglaNegocioError
from app.core.pagination import paginar_consulta
from app.core.tiempo import ahora_utc
from app.models import Consumo, EstadoReserva, Reserva
from app.schemas.consumo import ConsumoAnular, ConsumoCreate

ESTADOS_CON_CARGOS = {EstadoReserva.CHECK_IN}


class ConsumoYaAnuladoError(ConflictoError):
    codigo = "CONSUMO_YA_ANULADO"

    def __init__(self) -> None:
        super().__init__("El consumo ya fue anulado")


class ReservaNoPermiteCargosError(ReglaNegocioError):
    codigo = "RESERVA_NO_PERMITE_CARGOS"

    def __init__(self, estado: EstadoReserva) -> None:
        super().__init__(
            f"No se pueden registrar consumos en reserva con estado {estado.value}"
        )


def _obtener_reserva_o_404(db: Session, reserva_id: int) -> Reserva:
    reserva = db.get(Reserva, reserva_id)
    if reserva is None:
        raise NoEncontradoError("Reserva no encontrada")
    return reserva


def _obtener_consumo_o_404(db: Session, consumo_id: int, reserva_id: int) -> Consumo:
    consumo = db.get(Consumo, consumo_id)
    if consumo is None or consumo.reserva_id != reserva_id:
        raise NoEncontradoError("Consumo no encontrado")
    return consumo


def listar_consumos(
    db: Session,
    reserva_id: int,
    *,
    pagina: int = 1,
    tamano: int = 20,
    solo_vigentes: bool = False,
) -> tuple[list[Consumo], int]:
    _obtener_reserva_o_404(db, reserva_id)

    consulta = select(Consumo).where(Consumo.reserva_id == reserva_id)
    if solo_vigentes:
        consulta = consulta.where(Consumo.anulado.is_(False))

    total = db.scalar(
        select(func.count()).select_from(consulta.subquery())
    )
    items = list(
        db.scalars(
            paginar_consulta(
                consulta.order_by(Consumo.created_at.desc(), Consumo.id.desc()),
                pagina=pagina,
                tamano=tamano,
            )
        ).all()
    )
    return items, total or 0


def crear_consumo(
    db: Session,
    reserva_id: int,
    datos: ConsumoCreate,
    usuario_id: int,
) -> Consumo:
    reserva = _obtener_reserva_o_404(db, reserva_id)

    if reserva.estado not in ESTADOS_CON_CARGOS:
        raise ReservaNoPermiteCargosError(reserva.estado)

    consumo = Consumo(
        reserva_id=reserva_id,
        descripcion=datos.descripcion,
        cantidad=datos.cantidad,
        precio_unitario=datos.precio_unitario,
        registrado_por=usuario_id,
    )
    db.add(consumo)
    db.commit()
    db.refresh(consumo)
    return consumo


def anular_consumo(
    db: Session,
    reserva_id: int,
    consumo_id: int,
    datos: ConsumoAnular,
    usuario_id: int,
) -> Consumo:
    consumo = _obtener_consumo_o_404(db, consumo_id, reserva_id)

    if consumo.anulado:
        raise ConsumoYaAnuladoError()

    consumo.anulado = True
    consumo.anulado_por = usuario_id
    consumo.anulado_en = ahora_utc()
    consumo.motivo_anulacion = datos.motivo_anulacion
    db.commit()
    db.refresh(consumo)
    return consumo