"""Reglas de negocio de reservas: disponibilidad, creación, edición y consulta.

El código de reserva se genera con el formato `RES-{año}-{secuencial de 6 dígitos}`
donde el año viene de hoy en Bogotá. La unicidad la garantiza el constraint
UNIQUE de `reservas.codigo`; ante una colisión se recalcula y se reintenta.
"""

import re
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import (
    ConflictoError,
    NoEncontradoError,
    ReglaNegocioError,
    ValidacionError,
)
from app.core.pagination import paginar_consulta
from app.models import (
    EstadoHabitacion,
    EstadoReserva,
    Habitacion,
    Huesped,
    Reserva,
    TipoHabitacion,
)
from app.schemas.huesped import HuespedResumen
from app.schemas.reserva import (
    CancelarReservaRequest,
    HabitacionResumen,
    ReservaCreate,
    ReservaFiltros,
    ReservaRead,
    ReservaUpdate,
)
from app.services import auditoria_service

PATRON_CODIGO = re.compile(r"^RES-(\d{4})-(\d+)$")
MAX_INTENTOS_CODIGO = 5
ANCHO_SECUENCIAL = 6

# Estados que liberan la habitacion: no bloquean el rango para nuevas reservas.
ESTADOS_LIBERAN_HABITACION = (EstadoReserva.CANCELADA, EstadoReserva.NO_SHOW)
# Estados en los que la reserva todavia puede editarse.
ESTADOS_EDITABLES = (EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA)

# Transiciones de estado permitidas (clave = estado origen, valor = set de destinos).
TRANSICIONES_VALIDAS = {
    EstadoReserva.PENDIENTE: {EstadoReserva.CONFIRMADA, EstadoReserva.CANCELADA},
    EstadoReserva.CONFIRMADA: {EstadoReserva.CANCELADA, EstadoReserva.NO_SHOW},
}

# Acciones de auditoría para cada transición de estado de una reserva.
# Siguen la convención de verbo suelto usada en el resto del proyecto
# (CREATE/UPDATE en reservas, ANULAR en consumos y pagos).
ACCION_CONFIRMAR_RESERVA = "CONFIRMAR"
ACCION_CANCELAR_RESERVA = "CANCELAR"
ACCION_NO_SHOW_RESERVA = "NO_SHOW"


class TransicionInvalidaError(ReglaNegocioError):
    codigo = "TRANSICION_INVALIDA"

    def __init__(self, estado_actual: EstadoReserva, estado_pedido: EstadoReserva) -> None:
        super().__init__(
            f"Transicion invalida: de {estado_actual.value} a {estado_pedido.value}"
        )


class NoShowAntesDeFechaError(ReglaNegocioError):
    codigo = "NO_SHOW_ANTES_DE_FECHA"

    def __init__(self, fecha_entrada: date) -> None:
        super().__init__(
            f"No se puede marcar NO_SHOW antes de la fecha de entrada ({fecha_entrada.isoformat()})"
        )


class ReservaNoEncontradaError(NoEncontradoError):
    codigo = "RESERVA_NO_ENCONTRADA"

    def __init__(self) -> None:
        super().__init__("No se encontro la reserva")


class HuespedNoEncontradoError(NoEncontradoError):
    codigo = "HUESPED_NO_ENCONTRADO"

    def __init__(self) -> None:
        super().__init__("No se encontro el huesped")


class HabitacionNoEncontradaError(NoEncontradoError):
    codigo = "HABITACION_NO_ENCONTRADA"

    def __init__(self) -> None:
        super().__init__("No se encontro la habitacion")


class HabitacionInactivaError(ReglaNegocioError):
    codigo = "HABITACION_INACTIVA"

    def __init__(self) -> None:
        super().__init__("La habitacion no esta activa para recibir reservas")


class CapacidadExcedidaError(ConflictoError):
    codigo = "CAPACIDAD_EXCEDIDA"

    def __init__(self, capacidad: int, solicitados: int) -> None:
        super().__init__(
            f"La habitacion tiene capacidad para {capacidad} huespedes "
            f"y se solicitan {solicitados}"
        )


class ReservaSolapadaError(ConflictoError):
    codigo = "RESERVA_SOLAPADA"

    def __init__(self) -> None:
        super().__init__(
            "La habitacion ya tiene una reserva que se solapa con el rango indicado"
        )


class RangoFechasInvalidoError(ReglaNegocioError):
    codigo = "RANGO_FECHAS_INVALIDO"

    def __init__(self) -> None:
        super().__init__(
            "La fecha de salida debe ser posterior a la fecha de entrada"
        )


class EntradaEnPasadoError(ReglaNegocioError):
    codigo = "ENTRADA_EN_PASADO"

    def __init__(self, hoy: date) -> None:
        super().__init__(
            f"La fecha de entrada no puede ser anterior a hoy ({hoy.isoformat()})"
        )


class ReservaNoEditableError(ReglaNegocioError):
    codigo = "RESERVA_NO_EDITABLE"

    def __init__(self, estado: EstadoReserva) -> None:
        super().__init__(
            f"La reserva no es editable en estado {estado.value}"
        )


class CodigoReservaNoDisponibleError(ConflictoError):
    codigo = "CODIGO_RESERVA_NO_DISPONIBLE"

    def __init__(self) -> None:
        super().__init__(
            "No se pudo generar un codigo de reserva unico, intente de nuevo"
        )


class RangoDeFiltrosInvalidoError(ValidacionError):
    codigo = "RANGO_FILTROS_INVALIDO"

    def __init__(self) -> None:
        super().__init__(
            "La fecha desde no puede ser posterior a la fecha hasta",
            errors=[],
        )


def _habitacion_para_reserva(db: Session, habitacion_id: int) -> Habitacion:
    """Lee la habitacion bloqueando la fila (SELECT FOR UPDATE en PostgreSQL).

    En SQLite el bloqueo se ignora sin fallar; la unicidad y el no solapamiento
    se apoyan ademas en el constraint UNIQUE de `reservas.codigo` y en la
    comprobacion previa de solapamiento.
    """
    habitacion = db.get(Habitacion, habitacion_id, with_for_update=True)
    if habitacion is None:
        raise HabitacionNoEncontradaError
    return habitacion


def _validar_transicion(reserva: Reserva, destino: EstadoReserva) -> None:
    """Valida que `reserva` pueda pasar a `destino`.

    Lanza TransicionInvalidaError si la transición no está permitida desde el
    estado actual de la reserva.
    """
    destinos = TRANSICIONES_VALIDAS.get(reserva.estado)
    if destinos is None or destino not in destinos:
        raise TransicionInvalidaError(reserva.estado, destino)


def _es_activa(habitacion: Habitacion) -> bool:
    return habitacion.estado != EstadoHabitacion.MANTENIMIENTO


def _existe_solapamiento(
    db: Session,
    habitacion_id: int,
    fecha_entrada: date,
    fecha_salida: date,
    *,
    excluir_reserva_id: int | None = None,
) -> bool:
    """Indica si el rango [entrada, salida) se solapa con alguna reserva activa.

    El intervalo es semiabierto: una salida el mismo dia que otra entrada
    no se considera solapamiento.
    """
    consulta = select(Reserva.id).where(
        Reserva.habitacion_id == habitacion_id,
        Reserva.estado.not_in(ESTADOS_LIBERAN_HABITACION),
        Reserva.fecha_entrada < fecha_salida,
        Reserva.fecha_salida > fecha_entrada,
    )
    if excluir_reserva_id is not None:
        consulta = consulta.where(Reserva.id != excluir_reserva_id)
    return db.scalar(consulta.limit(1)) is not None


def _numero_noches(fecha_entrada: date, fecha_salida: date) -> int:
    return (fecha_salida - fecha_entrada).days


def _total_estimado(precio_noche: Decimal, noches: int) -> Decimal:
    return precio_noche * noches


def siguiente_numero_codigo(db: Session, anio: int) -> int:
    """Numero siguiente para `RES-{anio}-`, a partir del ultimo codigo existente.

    Se ordena por longitud y luego alfabeticamente para tolerar codigos con
    distinto ancho; el numero se interpreta en Python. Si no hay filas, o el
    ultimo codigo no sigue el formato, se reinicia en 1.
    """
    ultimo = db.scalar(
        select(Reserva.codigo)
        .where(Reserva.codigo.like(f"RES-{anio}-%"))
        .order_by(func.length(Reserva.codigo).desc(), Reserva.codigo.desc())
        .limit(1)
    )
    if ultimo is None:
        return 1
    coincidencia = PATRON_CODIGO.match(ultimo)
    if coincidencia is None or int(coincidencia.group(1)) != anio:
        return 1
    return int(coincidencia.group(2)) + 1


def generar_codigo(db: Session, anio: int) -> str:
    numero = siguiente_numero_codigo(db, anio)
    return f"RES-{anio}-{numero:0{ANCHO_SECUENCIAL}d}"


def _armar_lectura(
    reserva: Reserva, huesped: Huesped, habitacion: Habitacion
) -> ReservaRead:
    return ReservaRead(
        id=reserva.id,
        codigo=reserva.codigo,
        huesped=HuespedResumen.model_validate(huesped),
        habitacion=HabitacionResumen.model_validate(habitacion),
        fecha_entrada=reserva.fecha_entrada,
        fecha_salida=reserva.fecha_salida,
        numero_huespedes=reserva.numero_huespedes,
        estado=reserva.estado,
        precio_noche_aplicado=reserva.precio_noche_aplicado,
        total_estimado=reserva.total_estimado,
        observaciones=reserva.observaciones,
        motivo_cancelacion=reserva.motivo_cancelacion,
        check_in_real=reserva.check_in_real,
        check_out_real=reserva.check_out_real,
        creada_por=reserva.creada_por,
        created_at=reserva.created_at,
        updated_at=reserva.updated_at,
    )


def _armar_lecturas(db: Session, reservas: list[Reserva]) -> list[ReservaRead]:
    """Construye las lecturas resolviendo huesped y habitacion en dos consultas."""
    if not reservas:
        return []
    huespedes = {
        huesped.id: huesped
        for huesped in db.scalars(
            select(Huesped).where(
                Huesped.id.in_({reserva.huesped_id for reserva in reservas})
            )
        ).all()
    }
    habitaciones = {
        habitacion.id: habitacion
        for habitacion in db.scalars(
            select(Habitacion).where(
                Habitacion.id.in_({reserva.habitacion_id for reserva in reservas})
            )
        ).all()
    }
    return [
        _armar_lectura(
            reserva,
            huespedes[reserva.huesped_id],
            habitaciones[reserva.habitacion_id],
        )
        for reserva in reservas
    ]


def consultar_disponibilidad(
    db: Session,
    *,
    entrada: date,
    salida: date,
    huespedes: int = 1,
    tipo: TipoHabitacion | None = None,
) -> list[HabitacionResumen]:
    """Habitaciones activas libres para el rango semiabierto [entrada, salida)."""
    if salida <= entrada:
        raise RangoFechasInvalidoError

    ocupadas = (
        select(Reserva.habitacion_id)
        .where(
            Reserva.estado.not_in(ESTADOS_LIBERAN_HABITACION),
            Reserva.fecha_entrada < salida,
            Reserva.fecha_salida > entrada,
        )
        .distinct()
    )
    consulta = (
        select(Habitacion)
        .where(
            Habitacion.estado != EstadoHabitacion.MANTENIMIENTO,
            Habitacion.capacidad >= huespedes,
            Habitacion.id.not_in(ocupadas),
        )
        .order_by(Habitacion.numero)
    )
    if tipo is not None:
        consulta = consulta.where(Habitacion.tipo == tipo)

    habitaciones = list(db.scalars(consulta).all())
    return [HabitacionResumen.model_validate(habitacion) for habitacion in habitaciones]


def crear_reserva(
    db: Session,
    datos: ReservaCreate,
    usuario_id: int,
    hoy: date,
) -> ReservaRead:
    """Crea la reserva en PENDIENTE con el precio de la habitacion congelado.

    El precio_noche_aplicado se toma de la tarifa vigente al momento de crear y
    el total_estimado es noches × precio_noche_aplicado.
    """
    if datos.fecha_salida <= datos.fecha_entrada:
        raise RangoFechasInvalidoError
    if datos.fecha_entrada < hoy:
        raise EntradaEnPasadoError(hoy)

    huesped = db.get(Huesped, datos.huesped_id)
    if huesped is None:
        raise HuespedNoEncontradoError

    habitacion = _habitacion_para_reserva(db, datos.habitacion_id)
    if not _es_activa(habitacion):
        raise HabitacionInactivaError
    if habitacion.capacidad < datos.numero_huespedes:
        raise CapacidadExcedidaError(habitacion.capacidad, datos.numero_huespedes)
    if _existe_solapamiento(
        db, habitacion.id, datos.fecha_entrada, datos.fecha_salida
    ):
        raise ReservaSolapadaError

    noches = _numero_noches(datos.fecha_entrada, datos.fecha_salida)
    total_estimado = _total_estimado(habitacion.precio_por_noche, noches)

    reserva = _insertar_con_codigo_unico(
        db,
        anio=hoy.year,
        huesped_id=datos.huesped_id,
        habitacion_id=datos.habitacion_id,
        fecha_entrada=datos.fecha_entrada,
        fecha_salida=datos.fecha_salida,
        numero_huespedes=datos.numero_huespedes,
        precio_noche_aplicado=habitacion.precio_por_noche,
        total_estimado=total_estimado,
        observaciones=datos.observaciones,
        usuario_id=usuario_id,
    )
    return _armar_lectura(reserva, huesped, habitacion)


def _insertar_con_codigo_unico(
    db: Session,
    *,
    anio: int,
    huesped_id: int,
    habitacion_id: int,
    fecha_entrada: date,
    fecha_salida: date,
    numero_huespedes: int,
    precio_noche_aplicado: Decimal,
    total_estimado: Decimal,
    observaciones: str | None,
    usuario_id: int,
) -> Reserva:
    """Inserta la reserva reintentando el codigo ante colisiones.

    Cada intento usa un savepoint. Si salta un IntegrityError se deshace el
    savepoint y se vuelve a comprobar el solapamiento: si ahora hay solapamiento
    la causa es la restriccion de exclusion (RESERVA_SOLAPADA); si no, es una
    colision de codigo y se recalcula para reintentar.
    """
    for intento in range(1, MAX_INTENTOS_CODIGO + 1):
        reserva = Reserva(
            codigo=generar_codigo(db, anio),
            huesped_id=huesped_id,
            habitacion_id=habitacion_id,
            fecha_entrada=fecha_entrada,
            fecha_salida=fecha_salida,
            numero_huespedes=numero_huespedes,
            estado=EstadoReserva.PENDIENTE,
            precio_noche_aplicado=precio_noche_aplicado,
            total_estimado=total_estimado,
            observaciones=observaciones,
            creada_por=usuario_id,
        )
        savepoint = db.begin_nested()
        try:
            db.add(reserva)
            db.flush()
            savepoint.commit()
        except IntegrityError as error:
            savepoint.rollback()
            if _existe_solapamiento(
                db, habitacion_id, fecha_entrada, fecha_salida
            ):
                raise ReservaSolapadaError from error
            if intento == MAX_INTENTOS_CODIGO:
                raise CodigoReservaNoDisponibleError from error
            continue
        db.commit()
        db.refresh(reserva)
        return reserva

    raise CodigoReservaNoDisponibleError


def listar_reservas(db: Session, filtros: ReservaFiltros) -> tuple[list[ReservaRead], int]:
    """Lista reservas filtradas y paginadas, de la entrada mas reciente a la antigua."""
    if (
        filtros.desde is not None
        and filtros.hasta is not None
        and filtros.desde > filtros.hasta
    ):
        raise RangoDeFiltrosInvalidoError

    consulta = select(Reserva)
    if filtros.estado is not None:
        consulta = consulta.where(Reserva.estado == filtros.estado)
    if filtros.habitacion_id is not None:
        consulta = consulta.where(Reserva.habitacion_id == filtros.habitacion_id)
    if filtros.huesped_id is not None:
        consulta = consulta.where(Reserva.huesped_id == filtros.huesped_id)
    if filtros.desde is not None:
        consulta = consulta.where(Reserva.fecha_entrada >= filtros.desde)
    if filtros.hasta is not None:
        consulta = consulta.where(Reserva.fecha_entrada <= filtros.hasta)

    total = db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    reservas = list(
        db.scalars(
            paginar_consulta(
                consulta.order_by(Reserva.fecha_entrada.desc(), Reserva.id.desc()),
                pagina=filtros.pagina,
                tamano=filtros.tamano,
            )
        ).all()
    )
    return _armar_lecturas(db, reservas), total


def obtener_reserva(db: Session, reserva_id: int) -> ReservaRead:
    reserva = db.get(Reserva, reserva_id)
    if reserva is None:
        raise ReservaNoEncontradaError
    return _armar_lecturas(db, [reserva])[0]


def actualizar_reserva(
    db: Session,
    reserva_id: int,
    datos: ReservaUpdate,
    usuario_id: int,
    hoy: date,
) -> ReservaRead:
    """Actualiza una reserva editable.

    Solo se admiten los estados PENDIENTE y CONFIRMADA. Se revalidan huesped,
    habitacion, capacidad y solapamiento excluyendo la propia reserva.

    La entrada no puede quedar en el pasado, pero ese chequeo solo aplica cuando
    la fecha de entrada cambia de verdad: una reserva ya iniciada se puede
    seguir editando (observaciones, huespedes) y reenviar su entrada original,
    aunque ya sea anterior a hoy.

    Si cambian las fechas o la habitacion, el precio_noche_aplicado se vuelve a
    congelar con la tarifa vigente en ese momento (no se conserva el precio
    original) y el total_estimado se recalcula como noches × precio_noche_aplicado.
    Si solo cambian el huesped, los huespedes o las observaciones, el precio
    congelado y el total se mantienen.
    """
    reserva = db.get(Reserva, reserva_id)
    if reserva is None:
        raise ReservaNoEncontradaError
    if reserva.estado not in ESTADOS_EDITABLES:
        raise ReservaNoEditableError(reserva.estado)

    fecha_entrada = datos.fecha_entrada or reserva.fecha_entrada
    fecha_salida = datos.fecha_salida or reserva.fecha_salida
    numero_huespedes = datos.numero_huespedes or reserva.numero_huespedes
    habitacion_id = datos.habitacion_id or reserva.habitacion_id

    if fecha_salida <= fecha_entrada:
        raise RangoFechasInvalidoError
    if (
        datos.fecha_entrada is not None
        and datos.fecha_entrada != reserva.fecha_entrada
        and fecha_entrada < hoy
    ):
        raise EntradaEnPasadoError(hoy)

    huesped_id = datos.huesped_id or reserva.huesped_id
    huesped = db.get(Huesped, huesped_id)
    if huesped is None:
        raise HuespedNoEncontradoError

    habitacion = _habitacion_para_reserva(db, habitacion_id)
    if not _es_activa(habitacion):
        raise HabitacionInactivaError
    if habitacion.capacidad < numero_huespedes:
        raise CapacidadExcedidaError(habitacion.capacidad, numero_huespedes)
    if _existe_solapamiento(
        db,
        habitacion_id,
        fecha_entrada,
        fecha_salida,
        excluir_reserva_id=reserva_id,
    ):
        raise ReservaSolapadaError

    cambian_fechas_o_habitacion = (
        fecha_entrada != reserva.fecha_entrada
        or fecha_salida != reserva.fecha_salida
        or habitacion_id != reserva.habitacion_id
    )

    if datos.huesped_id is not None:
        reserva.huesped_id = datos.huesped_id
    if datos.habitacion_id is not None:
        reserva.habitacion_id = datos.habitacion_id
    reserva.fecha_entrada = fecha_entrada
    reserva.fecha_salida = fecha_salida
    reserva.numero_huespedes = numero_huespedes
    if datos.observaciones is not None:
        reserva.observaciones = datos.observaciones

    if cambian_fechas_o_habitacion:
        noches = _numero_noches(fecha_entrada, fecha_salida)
        reserva.precio_noche_aplicado = habitacion.precio_por_noche
        reserva.total_estimado = _total_estimado(habitacion.precio_por_noche, noches)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ReservaSolapadaError from error
    db.refresh(reserva)
    return _armar_lectura(reserva, huesped, habitacion)


def _cambiar_estado_y_auditar(
    db: Session,
    reserva: Reserva,
    habitacion: Habitacion,
    destino: EstadoReserva,
    accion: str,
    usuario_id: int,
    motivo: str | None = None,
) -> ReservaRead:
    """Cambia el estado de la reserva y registra la auditoría en una sola transacción.

    La auditoría se atribuye a `usuario_id` (el usuario autenticado que ejecuta la
    acción), nunca a `reserva.creada_por`. Si el cambio o el registro de auditoría
    fallan, se revierte todo y la reserva conserva su estado anterior.
    """
    estado_anterior = reserva.estado
    try:
        reserva.estado = destino
        if motivo is not None:
            reserva.motivo_cancelacion = motivo

        auditoria_service.registrar_auditoria(
            db,
            usuario_id=usuario_id,
            accion=accion,
            entidad="Reserva",
            entidad_id=reserva.id,
            detalle={
                "estado_anterior": estado_anterior.value,
                "estado_nuevo": destino.value,
            },
            commit=False,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(reserva)
    huesped = db.get(Huesped, reserva.huesped_id)
    return _armar_lectura(reserva, huesped, habitacion)


def confirmar_reserva(
    db: Session,
    reserva_id: int,
    usuario_id: int,
    hoy: date,
) -> ReservaRead:
    """Confirma una reserva PENDIENTE -> CONFIRMADA.

    Revalida que la habitacion siga activa y que no haya solapamiento
    (excluyendo la propia reserva). La entrada no puede ser anterior a hoy.
    """
    reserva = db.get(Reserva, reserva_id)
    if reserva is None:
        raise ReservaNoEncontradaError

    # Validar transición
    _validar_transicion(reserva, EstadoReserva.CONFIRMADA)

    # Bloquear habitación y recargar reserva
    habitacion = _habitacion_para_reserva(db, reserva.habitacion_id)
    db.refresh(
        reserva,
        attribute_names=["estado", "fecha_entrada", "fecha_salida", "habitacion_id"],
    )

    # Revalidar habitación activa
    if not _es_activa(habitacion):
        raise HabitacionInactivaError

    # Revalidar solapamiento excluyendo la propia reserva
    if _existe_solapamiento(
        db,
        habitacion.id,
        reserva.fecha_entrada,
        reserva.fecha_salida,
        excluir_reserva_id=reserva.id,
    ):
        raise ReservaSolapadaError

    # Entrada en el pasado (incluye misma fecha? El mismo día SÍ se permite)
    if reserva.fecha_entrada < hoy:
        raise EntradaEnPasadoError(hoy)

    return _cambiar_estado_y_auditar(
        db,
        reserva,
        habitacion,
        EstadoReserva.CONFIRMADA,
        ACCION_CONFIRMAR_RESERVA,
        usuario_id,
    )


def cancelar_reserva(
    db: Session,
    reserva_id: int,
    datos: CancelarReservaRequest,
    usuario_id: int,
) -> ReservaRead:
    """Cancela una reserva PENDIENTE|CONFIRMADA -> CANCELADA.

    Guarda el motivo en motivo_cancelacion. La habitación queda libre.
    """
    reserva = db.get(Reserva, reserva_id)
    if reserva is None:
        raise ReservaNoEncontradaError

    # Validar transición
    _validar_transicion(reserva, EstadoReserva.CANCELADA)

    # Bloquear habitación y recargar reserva
    habitacion = _habitacion_para_reserva(db, reserva.habitacion_id)
    db.refresh(reserva, attribute_names=["estado"])

    # Motivo ya viene validado y stripeado por el schema
    motivo = datos.motivo

    return _cambiar_estado_y_auditar(
        db,
        reserva,
        habitacion,
        EstadoReserva.CANCELADA,
        ACCION_CANCELAR_RESERVA,
        usuario_id,
        motivo=motivo,
    )


def no_show_reserva(
    db: Session,
    reserva_id: int,
    usuario_id: int,
    hoy: date,
) -> ReservaRead:
    """Marca una reserva CONFIRMADA -> NO_SHOW.

    Solo se permite si hoy >= fecha_entrada. La habitación queda libre.
    """
    reserva = db.get(Reserva, reserva_id)
    if reserva is None:
        raise ReservaNoEncontradaError

    # Validar transición PRIMERO
    _validar_transicion(reserva, EstadoReserva.NO_SHOW)

    # Luego validar fecha
    if hoy < reserva.fecha_entrada:
        raise NoShowAntesDeFechaError(reserva.fecha_entrada)

    # Bloquear habitación y recargar reserva
    habitacion = _habitacion_para_reserva(db, reserva.habitacion_id)
    db.refresh(reserva, attribute_names=["estado", "fecha_entrada"])

    return _cambiar_estado_y_auditar(
        db,
        reserva,
        habitacion,
        EstadoReserva.NO_SHOW,
        ACCION_NO_SHOW_RESERVA,
        usuario_id,
    )
