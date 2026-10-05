from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.core.pagination import Pagina, PaginacionParams
from app.models import RolUsuario, Usuario
from app.schemas.pago import PagoAnular, PagoCreate, PagoRead
from app.services import auditoria_service, pago_service

router = APIRouter(prefix="/api/reservas/{reserva_id}/pagos", tags=["pagos"])

usuarios_autorizados = require_roles(RolUsuario.ADMIN, RolUsuario.RECEPCION)
solo_administradores = require_roles(RolUsuario.ADMIN)


@router.get(
    "",
    response_model=Pagina[PagoRead],
    summary="Listar pagos de una reserva",
    description=(
        "Devuelve la lista paginada de pagos asociados a la reserva. "
        "Incluye un filtro opcional para ver solo los vigentes (no anulados)."
    ),
    responses={
        200: {"description": "Pagina de pagos"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para consultar pagos"},
        404: {"description": "Reserva no encontrada"},
    },
)
def listar_pagos(
    reserva_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
    paginacion: Annotated[PaginacionParams, Depends()],
    solo_vigentes: Annotated[bool, Query(alias="soloVigentes")] = False,
) -> Pagina[PagoRead]:
    items, total = pago_service.listar_pagos(
        db,
        reserva_id,
        pagina=paginacion.pagina,
        tamano=paginacion.tamano,
        solo_vigentes=solo_vigentes,
    )
    return Pagina[PagoRead](
        items=items,
        total=total,
        pagina=paginacion.pagina,
        tamano=paginacion.tamano,
    )


@router.post(
    "",
    response_model=PagoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear pago en una reserva",
    description=(
        "Registra un nuevo pago en la reserva. "
        "Permitido en todos los estados excepto CANCELADA y NO_SHOW."
    ),
    responses={
        201: {"description": "Pago creado"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para crear pagos"},
        404: {"description": "Reserva no encontrada"},
        409: {"description": "Conflicto con el estado actual"},
        422: {"description": "Datos de pago invalidos"},
    },
)
def crear_pago(
    reserva_id: int,
    datos: PagoCreate,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
) -> PagoRead:
    try:
        pago = pago_service.crear_pago(db, reserva_id, datos, usuario.id)
    except pago_service.ReservaNoPermitePagosError:
        raise

    auditoria_service.registrar_auditoria(
        db,
        usuario_id=usuario.id,
        accion="CREATE",
        entidad="Pago",
        entidad_id=pago.id,
        detalle={
            "reserva_id": reserva_id,
            "monto": str(datos.monto),
            "metodo": datos.metodo.value,
            "tipo": datos.tipo.value,
            "referencia": datos.referencia,
        },
    )
    return pago


@router.post(
    "/{pago_id}/anular",
    response_model=PagoRead,
    summary="Anular un pago",
    description="Marca el pago como anulado sin borrar el registro. Requiere rol administrador.",
    responses={
        200: {"description": "Pago anulado"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Se requiere el rol administrador"},
        404: {"description": "Pago no encontrado o no pertenece a la reserva"},
        409: {"description": "El pago ya fue anulado"},
    },
)
def anular_pago(
    reserva_id: int,
    pago_id: int,
    datos: PagoAnular,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
) -> PagoRead:
    try:
        pago = pago_service.anular_pago(db, reserva_id, pago_id, datos, usuario.id)
    except pago_service.PagoYaAnuladoError:
        raise

    auditoria_service.registrar_auditoria(
        db,
        usuario_id=usuario.id,
        accion="ANULAR",
        entidad="Pago",
        entidad_id=pago.id,
        detalle={
            "reserva_id": reserva_id,
            "motivo_anulacion": datos.motivo_anulacion,
        },
    )
    return pago