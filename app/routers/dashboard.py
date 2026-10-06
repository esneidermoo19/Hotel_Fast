from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.core.tiempo import obtener_hoy
from app.models import RolUsuario, Usuario
from app.schemas.dashboard import DashboardRead
from app.services import dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

usuarios_autorizados = require_roles(RolUsuario.ADMIN, RolUsuario.RECEPCION)


@router.get(
    "",
    response_model=DashboardRead,
    summary="Resumen operativo del hotel",
    description=(
        "Devuelve los indicadores del dia para operar el hotel: reservas "
        "activas, reservas pendientes de check-in, huespedes alojados, "
        "check-outs del dia, habitaciones disponibles, ocupadas y en "
        "mantenimiento, y cuentas con saldo pendiente. Usa los estados y las "
        "cuentas que ya existen, sin tablas nuevas."
    ),
    responses={
        200: {"description": "Resumen operativo del hotel"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para consultar el dashboard"},
    },
)
def obtener_resumen_dashboard(
    db: Annotated[Session, Depends(get_db)],
    hoy: Annotated[date, Depends(obtener_hoy)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
) -> DashboardRead:
    return dashboard_service.resumen_dashboard(db, hoy)
