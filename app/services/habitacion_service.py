from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import EstadoHabitacion, EstadoLimpieza, Habitacion, TipoHabitacion
from app.schemas.habitacion import HabitacionCreate, HabitacionUpdate
from app.services.reserva_service import ejecutar_con_auditoria

# Accion de auditoria del cambio de estado de limpieza de una habitacion.
ACCION_LIMPIEZA_HABITACION = "LIMPIEZA"


class HabitacionNoEncontradaError(LookupError):
    def __init__(self) -> None:
        super().__init__("No se encontro la habitacion")


class NumeroHabitacionDuplicadoError(ValueError):
    def __init__(self, numero: int) -> None:
        super().__init__(f"Ya existe una habitacion con el numero {numero}")


class HabitacionConReservasFuturasError(ValueError):
    def __init__(self) -> None:
        super().__init__("No se puede eliminar una habitacion con reservas futuras")


def listar_habitaciones(
    db: Session,
    *,
    estado: EstadoHabitacion | None = None,
    tipo: TipoHabitacion | None = None,
    limpieza: EstadoLimpieza | None = None,
) -> list[Habitacion]:
    """Lista las habitaciones ordenadas por numero, con filtros opcionales.

    Un filtro en None no restringe. El resultado sigue siendo un arreglo
    completo (no paginado).
    """
    consulta = select(Habitacion).order_by(Habitacion.numero)
    if estado is not None:
        consulta = consulta.where(Habitacion.estado == estado)
    if tipo is not None:
        consulta = consulta.where(Habitacion.tipo == tipo)
    if limpieza is not None:
        consulta = consulta.where(Habitacion.limpieza == limpieza)
    return list(db.scalars(consulta).all())


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


def actualizar_limpieza(
    db: Session,
    habitacion_id: int,
    limpieza: EstadoLimpieza,
    usuario_id: int,
) -> Habitacion:
    """Cambia el estado de limpieza y lo deja registrado en la auditoría.

    Bloquea la fila con SELECT FOR UPDATE para no cruzarse con un check-in o
    check-out que esté cambiando la misma habitación. Se permite aunque la
    habitación esté OCUPADA, porque limpiar no depende de su estado operativo.

    El cambio y la auditoría se hacen en una sola transacción.
    """
    habitacion = db.get(Habitacion, habitacion_id, with_for_update=True)
    if habitacion is None:
        raise HabitacionNoEncontradaError

    limpieza_anterior = habitacion.limpieza

    def mutar() -> None:
        habitacion.limpieza = limpieza

    ejecutar_con_auditoria(
        db,
        mutar=mutar,
        detalle={
            "limpieza_anterior": limpieza_anterior.value,
            "limpieza_nueva": limpieza.value,
        },
        usuario_id=usuario_id,
        accion=ACCION_LIMPIEZA_HABITACION,
        entidad="Habitacion",
        entidad_id=habitacion.id,
    )

    db.refresh(habitacion)
    return habitacion


def eliminar_habitacion(db: Session, habitacion_id: int) -> None:
    habitacion = obtener_habitacion(db, habitacion_id)
    # El servicio de reservas podra lanzar esta excepcion cuando se incorpore.
    db.delete(habitacion)
    db.commit()