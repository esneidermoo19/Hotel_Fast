"""Registro de auditoría.

`detalle` se guarda como JSON (columna `JSON` de PostgreSQL) con los campos
sensibles reemplazados por `[REDACTADO]`, para no filtrar contraseñas ni
tokens en la bitácora.
"""

import logging
from datetime import UTC, date, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session, attributes

from app.core.errors import ValidacionError
from app.core.pagination import paginar_consulta
from app.models.auditoria import Auditoria

logger = logging.getLogger(__name__)
BOGOTA = ZoneInfo("America/Bogota")

# Campos que nunca deben quedar en el detalle de auditoría.
CAMPOS_SENSIBLES = {
    "password",
    "password_hash",
    "passwordActual",
    "passwordNuevo",
    "password_actual",
    "password_nuevo",
    "token",
    "refreshToken",
    "refresh_token",
}


def _redactar(datos: dict[str, Any]) -> dict[str, Any]:
    return {
        clave: "[REDACTADO]" if clave in CAMPOS_SENSIBLES else valor
        for clave, valor in datos.items()
    }


def registrar_auditoria(
    db: Session,
    *,
    usuario_id: int | None,
    accion: str,
    entidad: str,
    entidad_id: int | None = None,
    ip: str | None = None,
    detalle: dict[str, Any] | None = None,
    commit: bool = True,
) -> Auditoria:
    """Registra una acción sensible y devuelve la fila creada."""
    registro = Auditoria(
        usuario_id=usuario_id,
        accion=accion,
        entidad=entidad,
        entidad_id=entidad_id,
        ip=ip,
        detalle=_redactar(detalle) if detalle else None,
    )
    db.add(registro)
    if commit:
        db.commit()
        db.refresh(registro)
    return registro


def listar_auditoria(
    db: Session,
    *,
    pagina: int,
    tamano: int,
    entidad: str | None = None,
    entidad_id: int | None = None,
    accion: str | None = None,
    usuario_id: int | None = None,
    desde: date | None = None,
    hasta: date | None = None,
) -> tuple[list[Auditoria], int]:
    if desde is not None and hasta is not None and desde > hasta:
        raise ValidacionError(
            "La fecha desde no puede ser posterior a la fecha hasta",
            errors=[],
        )

    consulta = select(Auditoria)
    if entidad:
        consulta = consulta.where(Auditoria.entidad == entidad)
    if entidad_id is not None:
        consulta = consulta.where(Auditoria.entidad_id == entidad_id)
    if accion:
        consulta = consulta.where(Auditoria.accion == accion)
    if usuario_id is not None:
        consulta = consulta.where(Auditoria.usuario_id == usuario_id)
    if desde is not None:
        inicio_utc = datetime.combine(
            desde,
            time.min,
            tzinfo=BOGOTA,
        ).astimezone(UTC)
        consulta = consulta.where(Auditoria.created_at >= inicio_utc)
    if hasta is not None:
        fin_exclusivo_utc = datetime.combine(
            hasta + timedelta(days=1),
            time.min,
            tzinfo=BOGOTA,
        ).astimezone(UTC)
        consulta = consulta.where(Auditoria.created_at < fin_exclusivo_utc)

    total = db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    items = list(
        db.scalars(
            paginar_consulta(
                consulta.order_by(Auditoria.created_at.desc(), Auditoria.id.desc()),
                pagina=pagina,
                tamano=tamano,
            )
        ).all()
    )
    for item in items:
        if item.created_at.tzinfo is None:
            attributes.set_committed_value(
                item,
                "created_at",
                item.created_at.replace(tzinfo=UTC),
            )
    return items, total