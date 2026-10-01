import pytest
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models import (
    Auditoria,
    Consumo,
    Habitacion,
    HorarioEmpleado,
    Huesped,
    Pago,
    RefreshToken,
    Reserva,
    RolUsuario,
)
from tests.conftest import TestingSessionLocal, test_engine
from tests.factories import (
    crear_auditoria,
    crear_consumo,
    crear_habitacion,
    crear_huesped,
    crear_pago,
    crear_refresh_token,
    crear_reserva,
    crear_turno,
    crear_usuario,
)


@pytest.fixture
def db_session() -> Session:
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


def test_crear_uno_de_cada_modelo(db_session):
    usuario_admin = crear_usuario(
        db_session, username="admin", email="admin@test.com", role=RolUsuario.ADMIN
    )
    usuario_recepcion = crear_usuario(
        db_session,
        username="recepcion",
        email="recepcion@test.com",
        role=RolUsuario.RECEPCION,
    )

    habitacion = crear_habitacion(db_session, numero=101)
    assert isinstance(habitacion, Habitacion)
    assert habitacion.numero == 101
    assert habitacion.limpieza is not None

    huesped = crear_huesped(db_session, numero_documento="1111111111")
    assert isinstance(huesped, Huesped)
    assert huesped.nombres == "Juan"

    reserva = crear_reserva(
        db_session,
        huesped=huesped,
        habitacion=habitacion,
        usuario=usuario_recepcion,
    )
    assert isinstance(reserva, Reserva)
    assert reserva.codigo == "RES-2026-000001"
    assert reserva.huesped_id == huesped.id
    assert reserva.habitacion_id == habitacion.id

    consumo = crear_consumo(db_session, reserva=reserva, usuario=usuario_recepcion)
    assert isinstance(consumo, Consumo)
    assert consumo.reserva_id == reserva.id
    assert consumo.cantidad == 2

    pago = crear_pago(db_session, reserva=reserva, usuario=usuario_recepcion)
    assert isinstance(pago, Pago)
    assert pago.reserva_id == reserva.id
    assert pago.monto > 0

    turno = crear_turno(db_session, usuario=usuario_recepcion)
    assert isinstance(turno, HorarioEmpleado)
    assert turno.usuario_id == usuario_recepcion.id

    auditoria = crear_auditoria(db_session, usuario=usuario_admin)
    assert isinstance(auditoria, Auditoria)
    assert auditoria.usuario_id == usuario_admin.id
    assert auditoria.accion == "CREATE"

    refresh_token = crear_refresh_token(db_session, usuario=usuario_admin)
    assert isinstance(refresh_token, RefreshToken)
    assert refresh_token.usuario_id == usuario_admin.id
    assert len(refresh_token.token_hash) == 64