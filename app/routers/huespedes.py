from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.models import RolUsuario, TipoDocumento, Usuario
from app.schemas.huesped import (
    HuespedCreate,
    HuespedPagina,
    HuespedRead,
    HuespedUpdate,
    ReservaDeHuespedPagina,
)
from app.services import huesped_service

router = APIRouter(prefix="/api/huespedes", tags=["huespedes"])
usuarios_autorizados = require_roles(RolUsuario.ADMIN, RolUsuario.RECEPCION)
solo_administradores = require_roles(RolUsuario.ADMIN)


@router.get(
    "",
    response_model=HuespedPagina,
    summary="Listar huespedes",
    description="Lista paginada de huespedes con busqueda y filtros.",
    responses={200: {"description": "Pagina de huespedes"}},
)
def listar_huespedes(
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
    q: Annotated[str | None, Query(description="Texto en nombres, apellidos o documento")] = None,
    tipo_documento: Annotated[TipoDocumento | None, Query(alias="tipoDocumento")] = None,
    numero_documento: Annotated[str | None, Query(alias="numeroDocumento")] = None,
    pagina: Annotated[int, Query(ge=1)] = 1,
    tamano: Annotated[int, Query(ge=1, le=100)] = 20,
) -> HuespedPagina:
    items, total = huesped_service.listar_huespedes(
        db,
        q=q,
        tipo_documento=tipo_documento,
        numero_documento=numero_documento,
        pagina=pagina,
        tamano=tamano,
    )
    return HuespedPagina(items=items, total=total, pagina=pagina, tamano=tamano)


@router.get(
    "/{huesped_id}",
    response_model=HuespedRead,
    summary="Obtener huesped",
    description="Obtiene un huesped por su identificador.",
    responses={
        200: {"description": "Huesped encontrado"},
        404: {"description": "Huesped no encontrado"},
    },
)
def obtener_huesped(
    huesped_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
) -> HuespedRead:
    try:
        return huesped_service.obtener_huesped(db, huesped_id)
    except huesped_service.HuespedNoEncontradoError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post(
    "",
    response_model=HuespedRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear huesped",
    description="Registra un huesped nuevo con documento unico por tipo.",
    responses={
        201: {"description": "Huesped creado"},
        409: {"description": "Documento duplicado"},
    },
)
def crear_huesped(
    datos: HuespedCreate,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
) -> HuespedRead:
    try:
        return huesped_service.crear_huesped(db, datos)
    except huesped_service.HuespedDuplicadoError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.put(
    "/{huesped_id}",
    response_model=HuespedRead,
    summary="Actualizar huesped",
    description="Actualiza los datos de un huesped existente.",
    responses={
        200: {"description": "Huesped actualizado"},
        404: {"description": "Huesped no encontrado"},
        409: {"description": "Documento duplicado"},
    },
)
def actualizar_huesped(
    huesped_id: int,
    datos: HuespedUpdate,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
) -> HuespedRead:
    try:
        return huesped_service.actualizar_huesped(db, huesped_id, datos)
    except huesped_service.HuespedNoEncontradoError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except huesped_service.HuespedDuplicadoError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.delete(
    "/{huesped_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar huesped",
    description="Elimina un huesped solo si no tiene reservas. Solo ADMIN.",
    responses={
        204: {"description": "Huesped eliminado"},
        404: {"description": "Huesped no encontrado"},
        409: {"description": "El huesped tiene reservas"},
    },
)
def eliminar_huesped(
    huesped_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
) -> Response:
    try:
        huesped_service.eliminar_huesped(db, huesped_id)
    except huesped_service.HuespedNoEncontradoError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except huesped_service.HuespedConReservasError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{huesped_id}/reservas",
    response_model=ReservaDeHuespedPagina,
    summary="Listar reservas del huesped",
    description="Lista paginada de reservas del huesped por entrada descendente.",
    responses={
        200: {"description": "Pagina de reservas"},
        404: {"description": "Huesped no encontrado"},
    },
)
def listar_reservas_de_huesped(
    huesped_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
    pagina: Annotated[int, Query(ge=1)] = 1,
    tamano: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ReservaDeHuespedPagina:
    try:
        items, total = huesped_service.listar_reservas_de_huesped(
            db, huesped_id, pagina=pagina, tamano=tamano
        )
    except huesped_service.HuespedNoEncontradoError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return ReservaDeHuespedPagina(
        items=items, total=total, pagina=pagina, tamano=tamano
    )
