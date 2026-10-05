from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.core.pagination import Pagina, PaginacionParams
from app.models import RolUsuario, TipoDocumento, Usuario
from app.schemas.huesped import (
    HuespedCreate,
    HuespedRead,
    HuespedUpdate,
    ReservaDeHuespedRead,
)
from app.services import huesped_service

router = APIRouter(prefix="/api/huespedes", tags=["huespedes"])
usuarios_autorizados = require_roles(RolUsuario.ADMIN, RolUsuario.RECEPCION)
solo_administradores = require_roles(RolUsuario.ADMIN)


@router.get(
    "",
    response_model=Pagina[HuespedRead],
    summary="Listar huespedes",
    description="Lista paginada de huespedes con busqueda y filtros.",
    responses={
        200: {"description": "Pagina de huespedes"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para consultar huespedes"},
    },
)
def listar_huespedes(
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
    paginacion: Annotated[PaginacionParams, Depends()],
    q: Annotated[str | None, Query(description="Texto en nombres, apellidos o documento")] = None,
    tipo_documento: Annotated[TipoDocumento | None, Query(alias="tipoDocumento")] = None,
    numero_documento: Annotated[str | None, Query(alias="numeroDocumento")] = None,
) -> Pagina[HuespedRead]:
    items, total = huesped_service.listar_huespedes(
        db,
        q=q,
        tipo_documento=tipo_documento,
        numero_documento=numero_documento,
        pagina=paginacion.pagina,
        tamano=paginacion.tamano,
    )
    return Pagina[HuespedRead](
        items=items,
        total=total,
        pagina=paginacion.pagina,
        tamano=paginacion.tamano,
    )


@router.get(
    "/{huesped_id}",
    response_model=HuespedRead,
    summary="Obtener huesped",
    description="Obtiene un huesped por su identificador.",
    responses={
        200: {"description": "Huesped encontrado"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para consultar huespedes"},
        404: {"description": "Huesped no encontrado"},
    },
)
def obtener_huesped(
    huesped_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
) -> HuespedRead:
    return huesped_service.obtener_huesped(db, huesped_id)


@router.post(
    "",
    response_model=HuespedRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear huesped",
    description="Registra un huesped nuevo con documento unico por tipo.",
    responses={
        201: {"description": "Huesped creado"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para crear huespedes"},
        409: {"description": "Documento duplicado"},
    },
)
def crear_huesped(
    datos: HuespedCreate,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
) -> HuespedRead:
    return huesped_service.crear_huesped(db, datos)


@router.put(
    "/{huesped_id}",
    response_model=HuespedRead,
    summary="Actualizar huesped",
    description="Actualiza los datos de un huesped existente.",
    responses={
        200: {"description": "Huesped actualizado"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para actualizar huespedes"},
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
    return huesped_service.actualizar_huesped(db, huesped_id, datos)


@router.delete(
    "/{huesped_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar huesped",
    description="Elimina un huesped solo si no tiene reservas. Solo ADMIN.",
    responses={
        204: {"description": "Huesped eliminado"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Se requiere el rol administrador"},
        404: {"description": "Huesped no encontrado"},
        409: {"description": "El huesped tiene reservas"},
    },
)
def eliminar_huesped(
    huesped_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
) -> Response:
    huesped_service.eliminar_huesped(db, huesped_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{huesped_id}/reservas",
    response_model=Pagina[ReservaDeHuespedRead],
    summary="Listar reservas del huesped",
    description="Lista paginada de reservas del huesped por entrada descendente.",
    responses={
        200: {"description": "Pagina de reservas"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para consultar reservas"},
        404: {"description": "Huesped no encontrado"},
    },
)
def listar_reservas_de_huesped(
    huesped_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
    paginacion: Annotated[PaginacionParams, Depends()],
) -> Pagina[ReservaDeHuespedRead]:
    items, total = huesped_service.listar_reservas_de_huesped(
        db,
        huesped_id,
        pagina=paginacion.pagina,
        tamano=paginacion.tamano,
    )
    return Pagina[ReservaDeHuespedRead](
        items=items,
        total=total,
        pagina=paginacion.pagina,
        tamano=paginacion.tamano,
    )
