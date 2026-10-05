from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.core.pagination import Pagina, PaginacionParams
from app.models import RolUsuario, Usuario
from app.schemas.base import CamelCaseSchema
from app.services import auditoria_service

router = APIRouter(prefix="/api/auditoria", tags=["auditoria"])
solo_administradores = require_roles(RolUsuario.ADMIN)


class AuditoriaRead(CamelCaseSchema):
    id: int
    usuario_id: int | None
    accion: str
    entidad: str
    entidad_id: int | None
    ip: str | None
    detalle: dict[str, object] | None
    created_at: datetime


@router.get(
    "",
    response_model=Pagina[AuditoriaRead],
    summary="Listar auditoria",
    description="Consulta eventos recientes de auditoria con filtros opcionales.",
    responses={
        200: {"description": "Pagina de eventos de auditoria"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Se requiere el rol administrador"},
        422: {"description": "Rango de fechas o parametros de consulta invalidos"},
    },
)
def listar_auditoria(
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
    paginacion: Annotated[PaginacionParams, Depends()],
    entidad: str | None = None,
    entidad_id: Annotated[int | None, Query(alias="entidadId")] = None,
    accion: str | None = None,
    usuario_id: Annotated[
        int | None,
        Query(alias="usuarioId", description="Filtra por identificador de usuario"),
    ] = None,
    desde: Annotated[
        date | None,
        Query(description="Fecha inicial inclusiva en la zona America/Bogota"),
    ] = None,
    hasta: Annotated[
        date | None,
        Query(description="Fecha final inclusiva en la zona America/Bogota"),
    ] = None,
) -> Pagina[AuditoriaRead]:
    items, total = auditoria_service.listar_auditoria(
        db,
        pagina=paginacion.pagina,
        tamano=paginacion.tamano,
        entidad=entidad,
        entidad_id=entidad_id,
        accion=accion,
        usuario_id=usuario_id,
        desde=desde,
        hasta=hasta,
    )
    return Pagina[AuditoriaRead](
        items=items,
        total=total,
        pagina=paginacion.pagina,
        tamano=paginacion.tamano,
    )
