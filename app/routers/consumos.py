from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.core.pagination import Pagina, PaginacionParams
from app.models import RolUsuario, Usuario
from app.schemas.consumo import ConsumoAnular, ConsumoCreate, ConsumoRead
from app.services import auditoria_service, consumo_service

router = APIRouter(
    prefix="/api/reservas/{reserva_id}/consumos", tags=["consumos"]
)

usuarios_autorizados = require_roles(RolUsuario.ADMIN, RolUsuario.RECEPCION)
solo_administradores = require_roles(RolUsuario.ADMIN)


@router.get(
    "",
    response_model=Pagina[ConsumoRead],
    summary="Listar consumos de una reserva",
    description=(
        "Devuelve la lista paginada de consumos asociados a la reserva. "
        "Incluye un filtro opcional para ver solo los vigentes (no anulados)."
    ),
    responses={
        200: {"description": "Pagina de consumos"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para consultar consumos"},
        404: {"description": "Reserva no encontrada"},
    },
)
def listar_consumos(
    reserva_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
    paginacion: Annotated[PaginacionParams, Depends()],
    solo_vigentes: Annotated[bool, Query(alias="soloVigentes")] = False,
) -> Pagina[ConsumoRead]:
    items, total = consumo_service.listar_consumos(
        db,
        reserva_id,
        pagina=paginacion.pagina,
        tamano=paginacion.tamano,
        solo_vigentes=solo_vigentes,
    )
    return Pagina[ConsumoRead](
        items=items,
        total=total,
        pagina=paginacion.pagina,
        tamano=paginacion.tamano,
    )


@router.post(
    "",
    response_model=ConsumoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear consumo en una reserva",
    description=(
        "Registra un nuevo consumo (cargo) en la reserva. "
        "Solo permitido si la reserva esta en estado CHECK_IN."
    ),
    responses={
        201: {"description": "Consumo creado"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para crear consumos"},
        404: {"description": "Reserva no encontrada"},
        409: {"description": "Conflicto con el estado actual"},
        422: {"description": "Datos de consumo invalidos"},
    },
)
def crear_consumo(
    reserva_id: int,
    datos: ConsumoCreate,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
) -> ConsumoRead:
    try:
        consumo = consumo_service.crear_consumo(db, reserva_id, datos, usuario.id)
    except consumo_service.ReservaNoPermiteCargosError:
        raise

    auditoria_service.registrar_auditoria(
        db,
        usuario_id=usuario.id,
        accion="CREATE",
        entidad="Consumo",
        entidad_id=consumo.id,
        detalle={
            "reserva_id": reserva_id,
            "descripcion": datos.descripcion,
            "cantidad": datos.cantidad,
            "precio_unitario": str(datos.precio_unitario),
        },
    )
    return consumo


@router.post(
    "/{consumo_id}/anular",
    response_model=ConsumoRead,
    summary="Anular un consumo",
    description="Marca el consumo como anulado sin borrar el registro. Requiere rol administrador.",
    responses={
        200: {"description": "Consumo anulado"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Se requiere el rol administrador"},
        404: {"description": "Consumo no encontrado o no pertenece a la reserva"},
        409: {"description": "El consumo ya fue anulado"},
    },
)
def anular_consumo(
    reserva_id: int,
    consumo_id: int,
    datos: ConsumoAnular,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
) -> ConsumoRead:
    try:
        consumo = consumo_service.anular_consumo(
            db, reserva_id, consumo_id, datos, usuario.id
        )
    except consumo_service.ConsumoYaAnuladoError:
        raise

    auditoria_service.registrar_auditoria(
        db,
        usuario_id=usuario.id,
        accion="ANULAR",
        entidad="Consumo",
        entidad_id=consumo.id,
        detalle={
            "reserva_id": reserva_id,
            "motivo_anulacion": datos.motivo_anulacion,
        },
    )
    return consumo