from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.core.errors import ConflictoError, NoEncontradoError
from app.models import RolUsuario, Usuario
from app.schemas.habitacion import (
    HabitacionCreate,
    HabitacionEstado,
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
    description="Lista las habitaciones disponibles para la gestion hotelera.",
    responses={
        200: {"description": "Listado de habitaciones"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para consultar habitaciones"},
    },
)
def listar_habitaciones(
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
) -> list[HabitacionRead]:
    return habitacion_service.listar_habitaciones(db)


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
