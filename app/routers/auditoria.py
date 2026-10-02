from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.core.pagination import LIMITE_MAXIMO
from app.models import Auditoria, RolUsuario, Usuario
from app.schemas.base import CamelCaseSchema

router = APIRouter(prefix="/api/auditoria", tags=["auditoria"])
solo_administradores = require_roles(RolUsuario.ADMIN)

TAMANO_MAXIMO = 200


class AuditoriaRead(CamelCaseSchema):
    id: int
    usuario_id: int | None
    accion: str
    entidad: str
    entidad_id: int | None
    direccion_ip: str | None
    detalle: str | None
    created_at: datetime


@router.get("", response_model=list[AuditoriaRead])
def listar_auditoria(
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
    entidad: str | None = None,
    entidad_id: int | None = None,
    accion: str | None = None,
    limite: int = LIMITE_MAXIMO,
) -> list[AuditoriaRead]:
    """Bitácora en orden descendente; siempre acotada para no traer el histórico completo."""
    consulta = select(Auditoria).order_by(Auditoria.id.desc()).limit(
        min(limite, TAMANO_MAXIMO)
    )
    if entidad:
        consulta = consulta.where(Auditoria.entidad == entidad)
    if entidad_id is not None:
        consulta = consulta.where(Auditoria.entidad_id == entidad_id)
    if accion:
        consulta = consulta.where(Auditoria.accion == accion)
    return list(db.scalars(consulta).all())
