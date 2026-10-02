"""Registro de auditoría.

La auditoría nunca debe romper la operación principal: si falla el insert,
se revierte junto con la acción y se avisa por logging, pero el error
original manda.
"""

import json
import logging
from typing import Any

from sqlalchemy.orm import Session

from app.models.auditoria import Auditoria

logger = logging.getLogger(__name__)

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
    direccion_ip: str | None = None,
    detalle: dict[str, Any] | None = None,
    commit: bool = True,
) -> Auditoria:
    """Registra una acción sensible y devuelve la fila creada.

    `detalle` se guarda como JSON con los campos sensibles reemplazados por
    `[REDACTADO]`, para no filtrar contraseñas ni tokens en la bitácora.
    """
    registro = Auditoria(
        usuario_id=usuario_id,
        accion=accion,
        entidad=entidad,
        entidad_id=entidad_id,
        direccion_ip=direccion_ip,
        detalle=(
            json.dumps(_redactar(detalle), ensure_ascii=False, default=str)
            if detalle
            else None
        ),
    )
    db.add(registro)
    if commit:
        db.commit()
        db.refresh(registro)
    return registro
