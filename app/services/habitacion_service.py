import logging
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.core.errors import (
    FormatoImagenInvalidoError,
    ImagenMuyGrandeError,
    MaximoImagenesError,
    NoEncontradoError,
)
from app.models import (
    EstadoHabitacion,
    EstadoLimpieza,
    Habitacion,
    HabitacionImagen,
    TipoHabitacion,
)
from app.schemas.habitacion import HabitacionCreate, HabitacionUpdate
from app.services import auditoria_service
from app.services.reserva_service import ejecutar_con_auditoria

logger = logging.getLogger(__name__)

# Accion de auditoria del cambio de estado de limpieza de una habitacion.
ACCION_LIMPIEZA_HABITACION = "LIMPIEZA"

# Acciones de auditoria para la gestion de imagenes de habitaciones.
ACCION_SUBIR_IMAGEN = "CREAR"
ACCION_BORRAR_IMAGEN = "ELIMINAR"

# Limites y formatos permitidos para las imagenes.
MAX_TAMANO_IMAGEN = 5 * 1024 * 1024
MAX_IMAGENES_POR_HABITACION = 10
BLOQUE_LECTURA = 64 * 1024

FIRMA_JPEG = b"\xff\xd8\xff"
FIRMA_PNG = b"\x89PNG\r\n\x1a\n"
FIRMA_RIFF = b"RIFF"
FIRMA_WEBP = b"WEBP"


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
    consulta = consulta.options(selectinload(Habitacion.imagenes))
    return list(db.scalars(consulta).all())


def obtener_habitacion(db: Session, habitacion_id: int) -> Habitacion:
    habitacion = db.scalar(
        select(Habitacion)
        .options(selectinload(Habitacion.imagenes))
        .where(Habitacion.id == habitacion_id)
    )
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
    rutas = [imagen.ruta for imagen in habitacion.imagenes]
    # El servicio de reservas podra lanzar esta excepcion cuando se incorpore.
    db.delete(habitacion)
    db.commit()
    for ruta in rutas:
        _eliminar_archivo(ruta)


def _directorio_media() -> Path:
    directorio = Path(settings.media_dir)
    directorio.mkdir(parents=True, exist_ok=True)
    return directorio


def _eliminar_archivo(ruta: str) -> None:
    """Borra un archivo de medios de forma no bloqueante.

    Si el archivo no existe o no se puede eliminar, solo se registra un aviso
    para no romper la operacion que ya se confirmo en base de datos.
    """
    try:
        (Path(settings.media_dir) / ruta).unlink(missing_ok=True)
    except OSError as error:
        logger.warning("No se pudo eliminar el archivo %s: %s", ruta, error)


def _detectar_formato(contenido: bytes) -> str | None:
    if contenido.startswith(FIRMA_JPEG):
        return "jpg"
    if contenido.startswith(FIRMA_PNG):
        return "png"
    if (
        len(contenido) >= 12
        and contenido[:4] == FIRMA_RIFF
        and contenido[8:12] == FIRMA_WEBP
    ):
        return "webp"
    return None


def _leer_contenido(archivo: UploadFile) -> bytes:
    contenido = bytearray()
    while True:
        bloque = archivo.file.read(BLOQUE_LECTURA)
        if not bloque:
            break
        contenido.extend(bloque)
        if len(contenido) > MAX_TAMANO_IMAGEN:
            raise ImagenMuyGrandeError(
                "La imagen supera el tamano maximo permitido (5 MB)"
            )
    return bytes(contenido)


def _promover_principal(db: Session, habitacion_id: int) -> None:
    siguiente = db.scalar(
        select(HabitacionImagen)
        .where(HabitacionImagen.habitacion_id == habitacion_id)
        .order_by(HabitacionImagen.orden, HabitacionImagen.id)
    )
    if siguiente is not None:
        siguiente.es_principal = True


def subir_imagen(
    db: Session,
    habitacion_id: int,
    archivo: UploadFile,
    usuario_id: int,
) -> HabitacionImagen:
    habitacion = db.get(Habitacion, habitacion_id)
    if habitacion is None:
        raise NoEncontradoError("No se encontro la habitacion")

    contenido = _leer_contenido(archivo)
    extension = _detectar_formato(contenido)
    if extension is None:
        raise FormatoImagenInvalidoError(
            "El archivo debe ser una imagen JPEG, PNG o WEBP"
        )

    imagenes = list(
        db.scalars(
            select(HabitacionImagen).where(
                HabitacionImagen.habitacion_id == habitacion_id
            )
        ).all()
    )
    if len(imagenes) >= MAX_IMAGENES_POR_HABITACION:
        raise MaximoImagenesError(
            "La habitacion ya tiene el maximo de imagenes permitidas"
        )

    nombre = f"{uuid4().hex}.{extension}"
    (_directorio_media() / nombre).write_bytes(contenido)

    imagen = HabitacionImagen(
        habitacion_id=habitacion_id,
        ruta=nombre,
        orden=len(imagenes) + 1,
        es_principal=not imagenes,
    )
    db.add(imagen)
    db.flush()
    try:
        auditoria_service.registrar_auditoria(
            db,
            usuario_id=usuario_id,
            accion=ACCION_SUBIR_IMAGEN,
            entidad="HabitacionImagen",
            entidad_id=imagen.id,
            detalle={"habitacion_id": habitacion_id, "ruta": nombre},
            commit=False,
        )
        db.commit()
    except Exception:
        db.rollback()
        _eliminar_archivo(nombre)
        raise
    db.refresh(imagen)
    return imagen


def eliminar_imagen(
    db: Session,
    habitacion_id: int,
    imagen_id: int,
    usuario_id: int,
) -> None:
    imagen = db.scalar(
        select(HabitacionImagen).where(
            HabitacionImagen.id == imagen_id,
            HabitacionImagen.habitacion_id == habitacion_id,
        )
    )
    if imagen is None:
        raise NoEncontradoError("Imagen no encontrada")

    era_principal = imagen.es_principal
    ruta = imagen.ruta
    db.delete(imagen)
    db.flush()
    if era_principal:
        _promover_principal(db, habitacion_id)
    try:
        auditoria_service.registrar_auditoria(
            db,
            usuario_id=usuario_id,
            accion=ACCION_BORRAR_IMAGEN,
            entidad="HabitacionImagen",
            entidad_id=imagen_id,
            detalle={"habitacion_id": habitacion_id, "ruta": ruta},
            commit=False,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    _eliminar_archivo(ruta)


def marcar_imagen_principal(
    db: Session,
    habitacion_id: int,
    imagen_id: int,
) -> HabitacionImagen:
    habitacion = db.get(Habitacion, habitacion_id)
    if habitacion is None:
        raise NoEncontradoError("No se encontro la habitacion")

    imagen = db.scalar(
        select(HabitacionImagen).where(
            HabitacionImagen.id == imagen_id,
            HabitacionImagen.habitacion_id == habitacion_id,
        )
    )
    if imagen is None:
        raise NoEncontradoError("Imagen no encontrada")

    if not imagen.es_principal:
        otras = db.scalars(
            select(HabitacionImagen).where(
                HabitacionImagen.habitacion_id == habitacion_id,
                HabitacionImagen.es_principal.is_(True),
            )
        ).all()
        for otra in otras:
            otra.es_principal = False
        db.flush()
        imagen.es_principal = True
        db.commit()

    db.refresh(imagen)
    return imagen