from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
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


@router.get("", response_model=list[HabitacionRead])
def listar_habitaciones(
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
) -> list[HabitacionRead]:
    return habitacion_service.listar_habitaciones(db)


@router.get("/{habitacion_id}", response_model=HabitacionRead)
def obtener_habitacion(
    habitacion_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
) -> HabitacionRead:
    try:
        return habitacion_service.obtener_habitacion(db, habitacion_id)
    except habitacion_service.HabitacionNoEncontradaError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post(
    "",
    response_model=HabitacionRead,
    status_code=status.HTTP_201_CREATED,
)
def crear_habitacion(
    datos: HabitacionCreate,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
) -> HabitacionRead:
    try:
        return habitacion_service.crear_habitacion(db, datos)
    except habitacion_service.NumeroHabitacionDuplicadoError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.put("/{habitacion_id}", response_model=HabitacionRead)
def actualizar_habitacion(
    habitacion_id: int,
    datos: HabitacionUpdate,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
) -> HabitacionRead:
    try:
        return habitacion_service.actualizar_habitacion(db, habitacion_id, datos)
    except habitacion_service.HabitacionNoEncontradaError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except habitacion_service.NumeroHabitacionDuplicadoError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.patch("/{habitacion_id}/estado", response_model=HabitacionRead)
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
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.delete("/{habitacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_habitacion(
    habitacion_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
) -> Response:
    try:
        habitacion_service.eliminar_habitacion(db, habitacion_id)
    except habitacion_service.HabitacionNoEncontradaError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except habitacion_service.HabitacionConReservasFuturasError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)