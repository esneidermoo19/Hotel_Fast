from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import EstadoHabitacion, Habitacion
from app.schemas.habitacion import HabitacionCreate, HabitacionUpdate


class HabitacionNoEncontradaError(LookupError):
    def __init__(self) -> None:
        super().__init__("No se encontro la habitacion")


class NumeroHabitacionDuplicadoError(ValueError):
    def __init__(self, numero: int) -> None:
        super().__init__(f"Ya existe una habitacion con el numero {numero}")


class HabitacionConReservasFuturasError(ValueError):
    def __init__(self) -> None:
        super().__init__("No se puede eliminar una habitacion con reservas futuras")


def listar_habitaciones(db: Session) -> list[Habitacion]:
    return list(db.scalars(select(Habitacion).order_by(Habitacion.numero)).all())


def obtener_habitacion(db: Session, habitacion_id: int) -> Habitacion:
    habitacion = db.get(Habitacion, habitacion_id)
    if habitacion is None:
        raise HabitacionNoEncontradaError
    return habitacion


def _guardar_habitacion(db: Session, habitacion: Habitacion) -> Habitacion:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        existente = db.scalar(
            select(Habitacion.id).where(Habitacion.numero == habitacion.numero)
        )
        if existente is not None:
            raise NumeroHabitacionDuplicadoError(habitacion.numero) from error
        raise
    db.refresh(habitacion)
    return habitacion


def crear_habitacion(db: Session, datos: HabitacionCreate) -> Habitacion:
    existente = db.scalar(
        select(Habitacion.id).where(Habitacion.numero == datos.numero)
    )
    if existente is not None:
        raise NumeroHabitacionDuplicadoError(datos.numero)
    habitacion = Habitacion(**datos.model_dump())
    db.add(habitacion)
    return _guardar_habitacion(db, habitacion)


def actualizar_habitacion(
    db: Session,
    habitacion_id: int,
    datos: HabitacionUpdate,
) -> Habitacion:
    habitacion = obtener_habitacion(db, habitacion_id)
    existente = db.scalar(
        select(Habitacion.id).where(
            Habitacion.numero == datos.numero,
            Habitacion.id != habitacion_id,
        )
    )
    if existente is not None:
        raise NumeroHabitacionDuplicadoError(datos.numero)
    for campo, valor in datos.model_dump().items():
        setattr(habitacion, campo, valor)
    return _guardar_habitacion(db, habitacion)


def actualizar_estado_habitacion(
    db: Session,
    habitacion_id: int,
    estado: EstadoHabitacion,
) -> Habitacion:
    habitacion = obtener_habitacion(db, habitacion_id)
    habitacion.estado = estado
    return _guardar_habitacion(db, habitacion)


def eliminar_habitacion(db: Session, habitacion_id: int) -> None:
    habitacion = obtener_habitacion(db, habitacion_id)
    # El servicio de reservas podra lanzar esta excepcion cuando se incorpore.
    db.delete(habitacion)
    db.commit()