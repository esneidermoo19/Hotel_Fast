from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.core.errors import ConflictoError, NoEncontradoError
from app.models import (
    EstadoHabitacion,
    EstadoLimpieza,
    RolUsuario,
    TipoHabitacion,
    Usuario,
)
from app.schemas.habitacion import (
    HabitacionCreate,
    HabitacionEstado,
    HabitacionImagenRead,
    HabitacionLimpieza,
    HabitacionRead,
    HabitacionUpdate,
)
from app.services import habitacion_service

router = APIRouter(prefix="/api/habitaciones", tags=["habitaciones"])
usuarios_autorizados = require_roles(RolUsuario.ADMIN, RolUsuario.RECEPCION)
solo_administradores = require_roles(RolUsuario.ADMIN)


@router.get(
    "",
    response_model=list[HabitacionRead],
    summary="Listar habitaciones",
    description=(
        "Lista las habitaciones de la gestion hotelera, con filtros opcionales "
        "por estado, tipo y limpieza. Devuelve siempre un arreglo completo."
    ),
    responses={
        200: {"description": "Listado de habitaciones"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para consultar habitaciones"},
        422: {"description": "Filtro invalido (estado, tipo o limpieza)"},
    },
)
def listar_habitaciones(
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
    estado: Annotated[EstadoHabitacion | None, Query()] = None,
    tipo: Annotated[TipoHabitacion | None, Query()] = None,
    limpieza: Annotated[EstadoLimpieza | None, Query()] = None,
) -> list[HabitacionRead]:
    return habitacion_service.listar_habitaciones(
        db,
        estado=estado,
        tipo=tipo,
        limpieza=limpieza,
    )


@router.get(
    "/{habitacion_id}",
    response_model=HabitacionRead,
    summary="Obtener habitacion",
    description="Obtiene una habitacion por su identificador.",
    responses={
        200: {"description": "Habitacion encontrada"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para consultar habitaciones"},
        404: {"description": "Habitacion no encontrada"},
    },
)
def obtener_habitacion(
    habitacion_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
) -> HabitacionRead:
    try:
        return habitacion_service.obtener_habitacion(db, habitacion_id)
    except habitacion_service.HabitacionNoEncontradaError as error:
        raise NoEncontradoError(str(error)) from error


@router.post(
    "",
    response_model=HabitacionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear habitacion",
    description="Registra una habitacion nueva.",
    responses={
        201: {"description": "Habitacion creada"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Se requiere el rol administrador"},
        409: {"description": "El numero de habitacion ya existe"},
        422: {"description": "Datos de habitacion invalidos"},
    },
)
def crear_habitacion(
    datos: HabitacionCreate,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
) -> HabitacionRead:
    try:
        return habitacion_service.crear_habitacion(db, datos)
    except habitacion_service.NumeroHabitacionDuplicadoError as error:
        raise ConflictoError(str(error)) from error


@router.put(
    "/{habitacion_id}",
    response_model=HabitacionRead,
    summary="Actualizar habitacion",
    description="Actualiza los datos de una habitacion existente.",
    responses={
        200: {"description": "Habitacion actualizada"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Se requiere el rol administrador"},
        404: {"description": "Habitacion no encontrada"},
        409: {"description": "El numero de habitacion ya existe"},
        422: {"description": "Datos de habitacion invalidos"},
    },
)
def actualizar_habitacion(
    habitacion_id: int,
    datos: HabitacionUpdate,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
) -> HabitacionRead:
    try:
        return habitacion_service.actualizar_habitacion(db, habitacion_id, datos)
    except habitacion_service.HabitacionNoEncontradaError as error:
        raise NoEncontradoError(str(error)) from error
    except habitacion_service.NumeroHabitacionDuplicadoError as error:
        raise ConflictoError(str(error)) from error


@router.patch(
    "/{habitacion_id}/estado",
    response_model=HabitacionRead,
    summary="Actualizar estado de habitacion",
    description="Cambia el estado operativo de una habitacion.",
    responses={
        200: {"description": "Estado actualizado"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para cambiar el estado"},
        404: {"description": "Habitacion no encontrada"},
        422: {"description": "Estado de habitacion invalido"},
    },
)
def actualizar_estado_habitacion(
    habitacion_id: int,
    datos: HabitacionEstado,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
) -> HabitacionRead:
    try:
        return habitacion_service.actualizar_estado_habitacion(
            db,
            habitacion_id,
            datos.estado,
        )
    except habitacion_service.HabitacionNoEncontradaError as error:
        raise NoEncontradoError(str(error)) from error


@router.patch(
    "/{habitacion_id}/limpieza",
    response_model=HabitacionRead,
    summary="Actualizar limpieza de habitacion",
    description=(
        "Cambia el estado de limpieza de una habitacion. Se permite aunque la "
        "habitacion este OCUPADA."
    ),
    responses={
        200: {"description": "Limpieza actualizada"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para cambiar la limpieza"},
        404: {"description": "Habitacion no encontrada"},
        422: {"description": "Estado de limpieza invalido"},
    },
)
def actualizar_limpieza_habitacion(
    habitacion_id: int,
    datos: HabitacionLimpieza,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
) -> HabitacionRead:
    try:
        return habitacion_service.actualizar_limpieza(
            db,
            habitacion_id,
            datos.limpieza,
            usuario.id,
        )
    except habitacion_service.HabitacionNoEncontradaError as error:
        raise NoEncontradoError(str(error)) from error


@router.delete(
    "/{habitacion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar habitacion",
    description="Elimina una habitacion sin reservas futuras.",
    responses={
        204: {"description": "Habitacion eliminada"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Se requiere el rol administrador"},
        404: {"description": "Habitacion no encontrada"},
        409: {"description": "La habitacion tiene reservas futuras"},
    },
)
def eliminar_habitacion(
    habitacion_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
) -> Response:
    try:
        habitacion_service.eliminar_habitacion(db, habitacion_id)
    except habitacion_service.HabitacionNoEncontradaError as error:
        raise NoEncontradoError(str(error)) from error
    except habitacion_service.HabitacionConReservasFuturasError as error:
        raise ConflictoError(str(error)) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{habitacion_id}/imagenes",
    response_model=HabitacionImagenRead,
    status_code=status.HTTP_201_CREATED,
    summary="Subir imagen de habitacion",
    description=(
        "Sube una imagen (JPEG, PNG o WEBP, maximo 5 MB) a una habitacion. "
        "Si es la primera imagen, queda marcada como principal."
    ),
    responses={
        201: {"description": "Imagen subida"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Se requiere el rol administrador"},
        404: {"description": "Habitacion no encontrada"},
        409: {"description": "La habitacion ya alcanzo el maximo de imagenes"},
        422: {"description": "Formato no permitido o archivo demasiado grande"},
    },
)
def subir_imagen_habitacion(
    habitacion_id: int,
    archivo: Annotated[UploadFile, File(description="Archivo de imagen a subir")],
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
) -> HabitacionImagenRead:
    return habitacion_service.subir_imagen(db, habitacion_id, archivo, usuario.id)


@router.delete(
    "/{habitacion_id}/imagenes/{imagen_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar imagen de habitacion",
    description=(
        "Elimina una imagen de la habitacion y su archivo. Si era la principal, "
        "promueve otra imagen como principal."
    ),
    responses={
        204: {"description": "Imagen eliminada"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Se requiere el rol administrador"},
        404: {"description": "Habitacion o imagen no encontrada"},
    },
)
def eliminar_imagen_habitacion(
    habitacion_id: int,
    imagen_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
) -> Response:
    habitacion_service.eliminar_imagen(db, habitacion_id, imagen_id, usuario.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/{habitacion_id}/imagenes/{imagen_id}/principal",
    response_model=HabitacionImagenRead,
    summary="Marcar imagen principal",
    description="Marca una imagen de la habitacion como principal.",
    responses={
        200: {"description": "Imagen marcada como principal"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Se requiere el rol administrador"},
        404: {"description": "Habitacion o imagen no encontrada"},
    },
)
def marcar_imagen_principal(
    habitacion_id: int,
    imagen_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
) -> HabitacionImagenRead:
    return habitacion_service.marcar_imagen_principal(db, habitacion_id, imagen_id)
