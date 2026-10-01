from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import (
    Auditoria,
    Consumo,
    EstadoLimpieza,
    EstadoReserva,
    Habitacion,
    HorarioEmpleado,
    Huesped,
    MetodoPago,
    Pago,
    RefreshToken,
    Reserva,
    RolUsuario,
    TipoDocumento,
    TipoHabitacion,
    TipoPago,
    TipoTurno,
    Usuario,
)


def crear_usuario(
    db: Session,
    *,
    username: str = "testuser",
    email: str = "test@example.com",
    nombre: str = "Usuario Test",
    password: str = "test-password-123",
    role: RolUsuario = RolUsuario.RECEPCION,
    activo: bool = True,
) -> Usuario:
    user = Usuario(
        username=username,
        email=email,
        nombre=nombre,
        password_hash=hash_password(password),
        role=role,
        activo=activo,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def crear_habitacion(
    db: Session,
    *,
    numero: int = 101,
    tipo: TipoHabitacion = TipoHabitacion.DOBLE,
    capacidad: int = 2,
    precio_por_noche: Decimal = Decimal("150000.00"),
    estado = None,
    limpieza: EstadoLimpieza = EstadoLimpieza.LIMPIA,
    descripcion: str | None = "Habitación de prueba",
) -> Habitacion:
    from app.models import EstadoHabitacion
    habitacion = Habitacion(
        numero=numero,
        tipo=tipo,
        capacidad=capacidad,
        precio_por_noche=precio_por_noche,
        estado=estado or EstadoHabitacion.DISPONIBLE,
        limpieza=limpieza,
        descripcion=descripcion,
    )
    db.add(habitacion)
    db.commit()
    db.refresh(habitacion)
    return habitacion


def crear_huesped(
    db: Session,
    *,
    tipo_documento: TipoDocumento = TipoDocumento.CC,
    numero_documento: str = "1234567890",
    nombres: str = "Juan",
    apellidos: str = "Perez",
    email: str | None = "juan.perez@example.com",
    telefono: str | None = "3001234567",
    nacionalidad: str | None = "Colombiana",
    fecha_nacimiento: date | None = date(1990, 1, 15),
    direccion: str | None = "Calle 123 #45-67",
    observaciones: str | None = "Huesped de prueba",
) -> Huesped:
    huesped = Huesped(
        tipo_documento=tipo_documento,
        numero_documento=numero_documento,
        nombres=nombres,
        apellidos=apellidos,
        email=email,
        telefono=telefono,
        nacionalidad=nacionalidad,
        fecha_nacimiento=fecha_nacimiento,
        direccion=direccion,
        observaciones=observaciones,
    )
    db.add(huesped)
    db.commit()
    db.refresh(huesped)
    return huesped


def crear_reserva(
    db: Session,
    *,
    huesped: Huesped,
    habitacion: Habitacion,
    usuario: Usuario,
    codigo: str = "RES-2026-000001",
    fecha_entrada: date = date(2026, 10, 15),
    fecha_salida: date = date(2026, 10, 18),
    numero_huespedes: int = 2,
    estado: EstadoReserva = EstadoReserva.PENDIENTE,
    precio_noche_aplicado: Decimal = Decimal("150000.00"),
    total_estimado: Decimal = Decimal("450000.00"),
    observaciones: str | None = "Reserva de prueba",
    motivo_cancelacion: str | None = None,
    check_in_real: datetime | None = None,
    check_out_real: datetime | None = None,
) -> Reserva:
    reserva = Reserva(
        codigo=codigo,
        huesped_id=huesped.id,
        habitacion_id=habitacion.id,
        fecha_entrada=fecha_entrada,
        fecha_salida=fecha_salida,
        numero_huespedes=numero_huespedes,
        estado=estado,
        precio_noche_aplicado=precio_noche_aplicado,
        total_estimado=total_estimado,
        observaciones=observaciones,
        motivo_cancelacion=motivo_cancelacion,
        check_in_real=check_in_real,
        check_out_real=check_out_real,
        creada_por=usuario.id,
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


def crear_consumo(
    db: Session,
    *,
    reserva: Reserva,
    usuario: Usuario,
    descripcion: str = "Minibar",
    cantidad: int = 2,
    precio_unitario: Decimal = Decimal("25000.00"),
    anulado: bool = False,
) -> Consumo:
    consumo = Consumo(
        reserva_id=reserva.id,
        descripcion=descripcion,
        cantidad=cantidad,
        precio_unitario=precio_unitario,
        anulado=anulado,
        registrado_por=usuario.id,
    )
    db.add(consumo)
    db.commit()
    db.refresh(consumo)
    return consumo


def crear_pago(
    db: Session,
    *,
    reserva: Reserva,
    usuario: Usuario,
    monto: Decimal = Decimal("100000.00"),
    metodo: MetodoPago = MetodoPago.EFECTIVO,
    tipo: TipoPago = TipoPago.ABONO,
    referencia: str | None = "REF-001",
    anulado: bool = False,
    motivo_anulacion: str | None = None,
    fecha_pago: datetime | None = None,
) -> Pago:
    pago = Pago(
        reserva_id=reserva.id,
        monto=monto,
        metodo=metodo,
        tipo=tipo,
        referencia=referencia,
        anulado=anulado,
        motivo_anulacion=motivo_anulacion,
        fecha_pago=fecha_pago or datetime.now(),
        registrado_por=usuario.id,
    )
    db.add(pago)
    db.commit()
    db.refresh(pago)
    return pago


def crear_turno(
    db: Session,
    *,
    usuario: Usuario,
    fecha: date = date(2026, 10, 15),
    hora_inicio: time = time(7, 0),
    hora_fin: time = time(15, 0),
    tipo_turno: TipoTurno = TipoTurno.MANANA,
    notas: str | None = "Turno de prueba",
) -> HorarioEmpleado:
    turno = HorarioEmpleado(
        usuario_id=usuario.id,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        tipo_turno=tipo_turno,
        notas=notas,
    )
    db.add(turno)
    db.commit()
    db.refresh(turno)
    return turno


def crear_auditoria(
    db: Session,
    *,
    usuario: Usuario | None = None,
    accion: str = "CREATE",
    entidad: str = "Test",
    entidad_id: int | None = 1,
    detalle: dict | None = None,
    ip: str | None = "127.0.0.1",
) -> Auditoria:
    auditoria = Auditoria(
        usuario_id=usuario.id if usuario else None,
        accion=accion,
        entidad=entidad,
        entidad_id=entidad_id,
        detalle=detalle,
        ip=ip,
    )
    db.add(auditoria)
    db.commit()
    db.refresh(auditoria)
    return auditoria


def crear_refresh_token(
    db: Session,
    *,
    usuario: Usuario,
    token_hash: str = "a" * 64,
    familia_id: str = "00000000-0000-0000-0000-000000000000",
    expira_en: datetime | None = None,
    revocado_en: datetime | None = None,
    user_agent: str | None = "TestAgent",
) -> RefreshToken:
    token = RefreshToken(
        usuario_id=usuario.id,
        token_hash=token_hash,
        familia_id=familia_id,
        expira_en=expira_en or (datetime.now() + timedelta(days=30)),
        revocado_en=revocado_en,
        user_agent=user_agent,
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token