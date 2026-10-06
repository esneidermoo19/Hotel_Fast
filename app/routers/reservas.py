from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.core.pagination import Pagina, PaginacionParams
from app.core.tiempo import obtener_hoy
from app.models import EstadoReserva, RolUsuario, TipoHabitacion, Usuario
from app.schemas.reserva import (
    CancelarReservaRequest,
    ExtenderReservaRequest,
    HabitacionResumen,
    ReservaCreate,
    ReservaFiltros,
    ReservaRead,
    ReservaUpdate,
)
from app.services import auditoria_service, reserva_service

router = APIRouter(prefix="/api/reservas", tags=["reservas"])
usuarios_autorizados = require_roles(RolUsuario.ADMIN, RolUsuario.RECEPCION)


def _detalle_auditoria(lectura: ReservaRead) -> dict[str, object]:
    """Detalle de auditoria sin datos sensibles del huesped."""
    return {
        "codigo": lectura.codigo,
        "huesped_id": lectura.huesped.id,
        "habitacion_id": lectura.habitacion.id,
        "fecha_entrada": lectura.fecha_entrada.isoformat(),
        "fecha_salida": lectura.fecha_salida.isoformat(),
        "numero_huespedes": lectura.numero_huespedes,
        "estado": lectura.estado.value,
        "precio_noche_aplicado": str(lectura.precio_noche_aplicado),
        "total_estimado": str(lectura.total_estimado),
    }


@router.get(
    "/disponibilidad",
    response_model=list[HabitacionResumen],
    summary="Consultar disponibilidad de habitaciones",
    description=(
        "Lista las habitaciones activas que estan libres en el rango "
        "[entrada, salida). Una salida el mismo dia que otra entrada no se "
        "considera solapamiento. Las reservas CANCELADA y NO_SHOW no bloquean."
    ),
    responses={
        200: {"description": "Habitaciones disponibles para el rango"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para consultar disponibilidad"},
        409: {"description": "La fecha de salida no es posterior a la de entrada"},
        422: {"description": "Parametros de consulta invalidos"},
    },
)
def consultar_disponibilidad(
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
    entrada: Annotated[date, Query(description="Fecha de entrada de la estancia")],
    salida: Annotated[date, Query(description="Fecha de salida de la estancia")],
    huespedes: Annotated[
        int, Query(ge=1, description="Numero de huespedes requeridos")
    ] = 1,
    tipo: Annotated[
        TipoHabitacion | None, Query(description="Filtra por tipo de habitacion")
    ] = None,
) -> list[HabitacionResumen]:
    return reserva_service.consultar_disponibilidad(
        db,
        entrada=entrada,
        salida=salida,
        huespedes=huespedes,
        tipo=tipo,
    )


@router.post(
    "",
    response_model=ReservaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear reserva",
    description=(
        "Crea una reserva en estado PENDIENTE. Valida que el huesped y la "
        "habitacion existan, que la habitacion este activa, que tenga "
        "capacidad suficiente, que la salida sea posterior a la entrada, que la "
        "entrada no sea anterior a hoy en Bogota y que no haya solapamiento. "
        "El precio por noche queda congelado con la tarifa vigente."
    ),
    responses={
        201: {"description": "Reserva creada"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para crear reservas"},
        404: {"description": "Huesped o habitacion no encontrados"},
        409: {
            "description": (
                "Conflicto: habitacion inactiva, capacidad excedida, rango "
                "invalido, entrada en el pasado, reserva solapada o codigo no "
                "disponible"
            )
        },
        422: {"description": "Datos de la reserva invalidos"},
    },
)
def crear_reserva(
    datos: ReservaCreate,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
    hoy: Annotated[date, Depends(obtener_hoy)],
) -> ReservaRead:
    reserva = reserva_service.crear_reserva(db, datos, usuario.id, hoy)

    auditoria_service.registrar_auditoria(
        db,
        usuario_id=usuario.id,
        accion="CREATE",
        entidad="Reserva",
        entidad_id=reserva.id,
        detalle=_detalle_auditoria(reserva),
    )
    return reserva


@router.get(
    "",
    response_model=Pagina[ReservaRead],
    summary="Listar reservas",
    description=(
        "Lista las reservas de forma paginada, de la fecha de entrada mas "
        "reciente a la mas antigua, con filtros opcionales por estado, "
        "habitacion, huesped y rango de fechas de entrada."
    ),
    responses={
        200: {"description": "Pagina de reservas"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para consultar reservas"},
        422: {"description": "Parametros de consulta o rango de fechas invalidos"},
    },
)
def listar_reservas(
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
    paginacion: Annotated[PaginacionParams, Depends()],
    estado: Annotated[
        EstadoReserva | None, Query(description="Filtra por estado de la reserva")
    ] = None,
    habitacion_id: Annotated[
        int | None, Query(alias="habitacionId", description="Filtra por habitacion")
    ] = None,
    huesped_id: Annotated[
        int | None, Query(alias="huespedId", description="Filtra por huesped")
    ] = None,
    desde: Annotated[
        date | None,
        Query(description="Fecha de entrada minima incluida (America/Bogota)"),
    ] = None,
    hasta: Annotated[
        date | None,
        Query(description="Fecha de entrada maxima incluida (America/Bogota)"),
    ] = None,
) -> Pagina[ReservaRead]:
    items, total = reserva_service.listar_reservas(
        db,
        ReservaFiltros(
            pagina=paginacion.pagina,
            tamano=paginacion.tamano,
            estado=estado,
            habitacion_id=habitacion_id,
            huesped_id=huesped_id,
            desde=desde,
            hasta=hasta,
        ),
    )
    return Pagina[ReservaRead](
        items=items,
        total=total,
        pagina=paginacion.pagina,
        tamano=paginacion.tamano,
    )


@router.get(
    "/{reserva_id}",
    response_model=ReservaRead,
    summary="Obtener reserva",
    description=(
        "Obtiene una reserva por su identificador, con un resumen del huesped "
        "y de la habitacion."
    ),
    responses={
        200: {"description": "Reserva encontrada"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para consultar reservas"},
        404: {"description": "Reserva no encontrada"},
    },
)
def obtener_reserva(
    reserva_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
) -> ReservaRead:
    return reserva_service.obtener_reserva(db, reserva_id)


@router.put(
    "/{reserva_id}",
    response_model=ReservaRead,
    summary="Actualizar reserva",
    description=(
        "Actualiza una reserva que este en PENDIENTE o CONFIRMADA. Revalida "
        "huesped, habitacion, capacidad y solapamiento excluyendo la propia "
        "reserva. Si cambian las fechas o la habitacion, el precio por noche se "
        "recalcula con la tarifa vigente y el total se vuelve a calcular."
    ),
    responses={
        200: {"description": "Reserva actualizada"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para actualizar reservas"},
        404: {"description": "Reserva, huesped o habitacion no encontrados"},
        409: {
            "description": (
                "La reserva no es editable en su estado actual, o hay conflicto "
                "por capacidad, rango, entrada en el pasado o solapamiento"
            )
        },
        422: {"description": "Datos de la reserva invalidos"},
    },
)
def actualizar_reserva(
    reserva_id: int,
    datos: ReservaUpdate,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
    hoy: Annotated[date, Depends(obtener_hoy)],
) -> ReservaRead:
    lectura = reserva_service.actualizar_reserva(db, reserva_id, datos, usuario.id, hoy)

    auditoria_service.registrar_auditoria(
        db,
        usuario_id=usuario.id,
        accion="UPDATE",
        entidad="Reserva",
        entidad_id=lectura.id,
        detalle=_detalle_auditoria(lectura),
    )
    return lectura


@router.post(
    "/{reserva_id}/confirmar",
    response_model=ReservaRead,
    summary="Confirmar reserva",
    description=(
        "Cambia una reserva de PENDIENTE a CONFIRMADA. Revalida que la habitacion "
        "siga activa y que no haya solapamiento excluyendo la propia reserva. "
        "La fecha de entrada no puede ser anterior a hoy en Bogota."
    ),
    responses={
        200: {"description": "Reserva confirmada"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para confirmar reservas"},
        404: {"description": "Reserva no encontrada"},
        409: {
            "description": (
                "Transicion invalida (p.ej. de CANCELADA), habitacion inactiva, "
                "solapamiento con otra reserva, o fecha de entrada en el pasado"
            )
        },
    },
)
def confirmar_reserva(
    reserva_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
    hoy: Annotated[date, Depends(obtener_hoy)],
) -> ReservaRead:
    return reserva_service.confirmar_reserva(db, reserva_id, usuario.id, hoy)


@router.post(
    "/{reserva_id}/cancelar",
    response_model=ReservaRead,
    summary="Cancelar reserva",
    description=(
        "Cambia una reserva de PENDIENTE o CONFIRMADA a CANCELADA. "
        "Requiere un motivo de 3 a 500 caracteres (se recortan espacios). "
        "La habitacion queda libre para nuevas reservas."
    ),
    responses={
        200: {"description": "Reserva cancelada"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para cancelar reservas"},
        404: {"description": "Reserva no encontrada"},
        409: {"description": "Transicion invalida (p.ej. de CHECK_IN, NO_SHOW)"},
        422: {"description": "Motivo invalido (3-500 caracteres, sin solo espacios)"},
    },
)
def cancelar_reserva(
    reserva_id: int,
    datos: CancelarReservaRequest,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
) -> ReservaRead:
    return reserva_service.cancelar_reserva(db, reserva_id, datos, usuario.id)


@router.post(
    "/{reserva_id}/no-show",
    response_model=ReservaRead,
    summary="Marcar no-show",
    description=(
        "Cambia una reserva de CONFIRMADA a NO_SHOW. "
        "Solo permitido si hoy (en Bogota) es mayor o igual a la fecha de entrada. "
        "La habitacion queda libre para nuevas reservas."
    ),
    responses={
        200: {"description": "Reserva marcada como NO_SHOW"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para marcar no-show"},
        404: {"description": "Reserva no encontrada"},
        409: {
            "description": (
                "Transicion invalida (p.ej. de PENDIENTE, CANCELADA) o "
                "intento de no-show antes de la fecha de entrada"
            )
        },
    },
)
def no_show_reserva(
    reserva_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
    hoy: Annotated[date, Depends(obtener_hoy)],
) -> ReservaRead:
    return reserva_service.no_show_reserva(db, reserva_id, usuario.id, hoy)


@router.post(
    "/{reserva_id}/check-in",
    response_model=ReservaRead,
    summary="Registrar check-in",
    description=(
        "Cambia una reserva de CONFIRMADA a CHECK_IN y deja la habitacion OCUPADA. "
        "La fecha de entrada no puede ser posterior a hoy y la estancia no puede "
        "estar vencida. La habitacion debe estar DISPONIBLE y LIMPIA."
    ),
    responses={
        200: {"description": "Reserva en CHECK_IN"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para registrar check-in"},
        404: {"description": "Reserva no encontrada"},
        409: {
            "description": (
                "Transicion invalida (la reserva no esta CONFIRMADA), check-in "
                "antes de la fecha de entrada, estancia vencida o habitacion "
                "no lista (sucia, ocupada o en mantenimiento)"
            )
        },
    },
)
def check_in_reserva(
    reserva_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
    hoy: Annotated[date, Depends(obtener_hoy)],
) -> ReservaRead:
    return reserva_service.check_in_reserva(db, reserva_id, usuario.id, hoy)


@router.post(
    "/{reserva_id}/check-out",
    response_model=ReservaRead,
    summary="Registrar check-out",
    description=(
        "Cambia una reserva de CHECK_IN a CHECK_OUT y deja la habitacion SUCIA. "
        "No cambia la fecha de salida ni el total: lo facturado sigue siendo lo "
        "reservado."
    ),
    responses={
        200: {"description": "Reserva en CHECK_OUT"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para registrar check-out"},
        404: {"description": "Reserva no encontrada"},
        409: {"description": "Transicion invalida (la reserva no esta en CHECK_IN)"},
    },
)
def check_out_reserva(
    reserva_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
) -> ReservaRead:
    return reserva_service.check_out_reserva(db, reserva_id, usuario.id)


@router.post(
    "/{reserva_id}/extender",
    response_model=ReservaRead,
    summary="Extender estancia",
    description=(
        "Alarga la estancia de una reserva en CHECK_IN. La nueva fecha de salida "
        "debe ser posterior a la actual, no puede solaparse con otra reserva de la "
        "misma habitacion y recalcula el total como noches por el precio noche "
        "aplicado, sin cambiar el precio congelado. Por decision de negocio no "
        "valida el estado de la habitacion (puede seguir en mantenimiento mientras "
        "el huesped esta alojado) ni que la fecha de salida actual siga en el "
        "futuro: una estancia cuya salida ya paso tambien puede extenderse."
    ),
    responses={
        200: {"description": "Estancia extendida"},
        401: {"description": "Token de acceso invalido o ausente"},
        403: {"description": "Rol sin permisos para extender reservas"},
        404: {"description": "Reserva no encontrada"},
        409: {
            "description": (
                "Transicion invalida (la reserva no esta en CHECK_IN), rango de "
                "fechas invalido o solapamiento con otra reserva"
            )
        },
        422: {"description": "Nueva fecha de salida invalida"},
    },
)
def extender_reserva(
    reserva_id: int,
    datos: ExtenderReservaRequest,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuarios_autorizados)],
) -> ReservaRead:
    return reserva_service.extender_reserva(db, reserva_id, datos, usuario.id)