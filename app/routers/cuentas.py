from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.models import RolUsuario, Usuario
from app.schemas.cuenta import CuentaRead
from app.services import cuenta_service

router = APIRouter(prefix="/api/cuentas", tags=["cuentas"])

usuarios_autorizados = require_roles(RolUsuario.ADMIN, RolUsuario.RECEPCION)


@router.get(
    "/{reserva_id}",
    response_model=CuentaRead,
    summary="Obtener cuenta de una reserva",
    description=(
        "Devuelve el detalle completo de la cuenta de la reserva: "
        "total de alojamiento (noches x tarifa), consumos vigentes, "
        "pagos vigentes (excluye reembolsos), saldo pendiente y "
        "listado completo de consumos y pagos con su estado de anulación."
    ),
    responses={
        200: {"description": "Cuenta de la reserva"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para consultar la cuenta"},
        404: {"description": "Reserva no encontrada"},
    },
)
def obtener_cuenta(
    reserva_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
) -> CuentaRead:
    return cuenta_service.calcular_cuenta(db, reserva_id)