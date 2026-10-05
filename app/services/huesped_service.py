from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflictoError, NoEncontradoError
from app.core.pagination import paginar_consulta
from app.models import Huesped, Reserva, TipoDocumento
from app.schemas.huesped import HuespedCreate, HuespedUpdate


class HuespedNoEncontradoError(NoEncontradoError):
    def __init__(self) -> None:
        super().__init__("No se encontro el huesped")


class HuespedDuplicadoError(ConflictoError):
    def __init__(self, tipo_documento: TipoDocumento, numero: str) -> None:
        super().__init__(
            "HUESPED_DUPLICADO: ya existe un huesped "
            f"con {tipo_documento.value} {numero}"
        )


class HuespedConReservasError(ConflictoError):
    def __init__(self) -> None:
        super().__init__(
            "HUESPED_CON_RESERVAS: no se puede eliminar "
            "un huesped con reservas"
        )


def _existe_documento(
    db: Session,
    tipo_documento: TipoDocumento,
    numero_documento: str,
    excluir_id: int | None = None,
) -> bool:
    consulta = select(Huesped.id).where(
        Huesped.tipo_documento == tipo_documento,
        Huesped.numero_documento == numero_documento,
    )
    if excluir_id is not None:
        consulta = consulta.where(Huesped.id != excluir_id)
    return db.scalar(consulta) is not None


def listar_huespedes(
    db: Session,
    q: str | None = None,
    tipo_documento: TipoDocumento | None = None,
    numero_documento: str | None = None,
    pagina: int = 1,
    tamano: int = 20,
) -> tuple[list[Huesped], int]:
    consulta = select(Huesped)
    if q:
        patron = f"%{q.strip()}%"
        consulta = consulta.where(
            Huesped.nombres.ilike(patron)
            | Huesped.apellidos.ilike(patron)
            | Huesped.numero_documento.ilike(patron)
        )
    if tipo_documento is not None:
        consulta = consulta.where(Huesped.tipo_documento == tipo_documento)
    if numero_documento:
        consulta = consulta.where(
            Huesped.numero_documento == numero_documento.strip()
        )
    total = db.scalar(
        select(func.count()).select_from(consulta.subquery())
    )
    items = list(
        db.scalars(
            paginar_consulta(
                consulta.order_by(Huesped.id),
                pagina=pagina,
                tamano=tamano,
            )
        ).all()
    )
    return items, total or 0


def obtener_huesped(db: Session, huesped_id: int) -> Huesped:
    huesped = db.get(Huesped, huesped_id)
    if huesped is None:
        raise HuespedNoEncontradoError
    return huesped


def _guardar_huesped(db: Session, huesped: Huesped) -> Huesped:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HuespedDuplicadoError(
            huesped.tipo_documento, huesped.numero_documento
        ) from error
    db.refresh(huesped)
    return huesped


def crear_huesped(db: Session, datos: HuespedCreate) -> Huesped:
    if _existe_documento(db, datos.tipo_documento, datos.numero_documento):
        raise HuespedDuplicadoError(
            datos.tipo_documento, datos.numero_documento
        )
    huesped = Huesped(**datos.model_dump())
    db.add(huesped)
    return _guardar_huesped(db, huesped)


def actualizar_huesped(
    db: Session,
    huesped_id: int,
    datos: HuespedUpdate,
) -> Huesped:
    huesped = obtener_huesped(db, huesped_id)
    if _existe_documento(
        db, datos.tipo_documento, datos.numero_documento, excluir_id=huesped_id
    ):
        raise HuespedDuplicadoError(
            datos.tipo_documento, datos.numero_documento
        )
    for campo, valor in datos.model_dump().items():
        setattr(huesped, campo, valor)
    return _guardar_huesped(db, huesped)


def eliminar_huesped(db: Session, huesped_id: int) -> None:
    huesped = obtener_huesped(db, huesped_id)
    con_reservas = db.scalar(
        select(Reserva.id).where(Reserva.huesped_id == huesped_id).limit(1)
    )
    if con_reservas is not None:
        raise HuespedConReservasError
    db.delete(huesped)
    db.commit()


def listar_reservas_de_huesped(
    db: Session,
    huesped_id: int,
    pagina: int = 1,
    tamano: int = 20,
) -> tuple[list[Reserva], int]:
    obtener_huesped(db, huesped_id)
    consulta = select(Reserva).where(Reserva.huesped_id == huesped_id)
    total = db.scalar(
        select(func.count()).select_from(consulta.subquery())
    )
    items = list(
        db.scalars(
            paginar_consulta(
                consulta.order_by(Reserva.fecha_entrada.desc(), Reserva.id.desc()),
                pagina=pagina,
                tamano=tamano,
            )
        ).all()
    )
    return items, total or 0
