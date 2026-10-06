from datetime import UTC, date, datetime

import pytest
from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from app.core.tiempo import obtener_hoy
from app.main import app
from app.models import EstadoHabitacion, EstadoReserva
from app.routers.dashboard import router
from tests.factories import (
    crear_habitacion,
    crear_huesped,
    crear_pago,
    crear_reserva,
    crear_usuario,
)

HOY = date(2026, 10, 1)

VACIO = {
    "reservasActivas": 0,
    "reservasPendientesCheckIn": 0,
    "huespedesAlojados": 0,
    "checkOutsDelDia": 0,
    "habitacionesDisponibles": 0,
    "habitacionesOcupadas": 0,
    "habitacionesEnMantenimiento": 0,
    "cuentasConSaldoPendiente": 0,
}


@pytest.fixture
def hoy_fijo():
    """Fija hoy en Bogota para poder crear reservas con fechas concretas."""
    app.dependency_overrides[obtener_hoy] = lambda: HOY
    yield HOY
    app.dependency_overrides.pop(obtener_hoy, None)


def test_dashboard_router_prefix() -> None:
    assert router.prefix == "/api/dashboard"


def test_dashboard_sin_datos(client: TestClient, admin_headers: dict[str, str]) -> None:
    """Con la base vacia todos los indicadores son cero."""
    response = client.get("/api/dashboard", headers=admin_headers)

    assert response.status_code == 200
    assert response.json() == VACIO


def test_dashboard_resumen_operativo(
    client: TestClient, admin_headers: dict[str, str], hoy_fijo
) -> None:
    """Cuenta reservas, huespedes, habitaciones y cuentas con saldo pendiente."""
    db = TestingSessionLocal()
    try:
        usuario = crear_usuario(db, username="dash1", email="dash1@example.com")
        huesped = crear_huesped(db, numero_documento="7001")
        ocupada = crear_habitacion(
            db, numero=401, estado=EstadoHabitacion.OCUPADA
        )
        libre = crear_habitacion(db, numero=402)
        crear_habitacion(db, numero=403, estado=EstadoHabitacion.MANTENIMIENTO)

        # Pendiente sin pagos: activa, pendiente de check-in y con saldo.
        crear_reserva(
            db,
            huesped=huesped,
            habitacion=libre,
            usuario=usuario,
            codigo="RES-2026-000401",
            estado=EstadoReserva.PENDIENTE,
        )
        # Confirmada y pagada por completo: pendiente pero sin saldo.
        confirmada = crear_reserva(
            db,
            huesped=huesped,
            habitacion=libre,
            usuario=usuario,
            codigo="RES-2026-000402",
            estado=EstadoReserva.CONFIRMADA,
        )
        crear_pago(
            db,
            reserva=confirmada,
            usuario=usuario,
            monto=confirmada.total_estimado,
        )
        # Alojada con tres huespedes y sin pagos: con saldo.
        crear_reserva(
            db,
            huesped=huesped,
            habitacion=ocupada,
            usuario=usuario,
            codigo="RES-2026-000403",
            estado=EstadoReserva.CHECK_IN,
            numero_huespedes=3,
        )
        # Check-out de hoy: cuenta para el dia y sigue con saldo.
        crear_reserva(
            db,
            huesped=huesped,
            habitacion=libre,
            usuario=usuario,
            codigo="RES-2026-000404",
            estado=EstadoReserva.CHECK_OUT,
            check_out_real=datetime(2026, 10, 1, 15, 0, tzinfo=UTC),
        )
        # Check-out de ayer y pagado: no cuenta para el dia ni para el saldo.
        ayer = crear_reserva(
            db,
            huesped=huesped,
            habitacion=libre,
            usuario=usuario,
            codigo="RES-2026-000405",
            estado=EstadoReserva.CHECK_OUT,
            check_out_real=datetime(2026, 9, 30, 20, 0, tzinfo=UTC),
        )
        crear_pago(db, reserva=ayer, usuario=usuario, monto=ayer.total_estimado)
        # Cancelada: queda fuera de todo, tambien de las cuentas con saldo.
        crear_reserva(
            db,
            huesped=huesped,
            habitacion=libre,
            usuario=usuario,
            codigo="RES-2026-000406",
            estado=EstadoReserva.CANCELADA,
        )
    finally:
        db.close()

    response = client.get("/api/dashboard", headers=admin_headers)

    assert response.status_code == 200
    assert response.json() == {
        "reservasActivas": 3,  # PENDIENTE, CONFIRMADA y CHECK_IN
        "reservasPendientesCheckIn": 2,  # PENDIENTE y CONFIRMADA
        "huespedesAlojados": 3,  # personas de la reserva en CHECK_IN
        "checkOutsDelDia": 1,  # solo el de hoy; el de ayer no cuenta
        "habitacionesDisponibles": 1,  # la 402; la 401 esta ocupada
        "habitacionesOcupadas": 1,  # la 401
        "habitacionesEnMantenimiento": 1,  # la 403
        "cuentasConSaldoPendiente": 3,  # pendiente, alojada y saliente de hoy
    }


def test_dashboard_check_outs_del_dia_respetan_la_zona_horaria(
    client: TestClient, admin_headers: dict[str, str], hoy_fijo
) -> None:
    """El dia del check-out es el de Bogota, no el de UTC."""
    db = TestingSessionLocal()
    try:
        usuario = crear_usuario(db, username="dash2", email="dash2@example.com")
        huesped = crear_huesped(db, numero_documento="7002")
        habitacion = crear_habitacion(db, numero=411)

        casos = {
            "RES-2026-000411": datetime(2026, 10, 1, 15, 0, tzinfo=UTC),
            # 02/10 04:00 UTC todavia es 01/10 en Bogota.
            "RES-2026-000412": datetime(2026, 10, 2, 4, 0, tzinfo=UTC),
            # 30/09 20:00 UTC ya es 30/09 en Bogota.
            "RES-2026-000413": datetime(2026, 9, 30, 20, 0, tzinfo=UTC),
        }
        for codigo, momento in casos.items():
            crear_reserva(
                db,
                huesped=huesped,
                habitacion=habitacion,
                usuario=usuario,
                codigo=codigo,
                estado=EstadoReserva.CHECK_OUT,
                check_out_real=momento,
            )
    finally:
        db.close()

    response = client.get("/api/dashboard", headers=admin_headers)

    assert response.status_code == 200
    assert response.json()["checkOutsDelDia"] == 2


@pytest.mark.parametrize("headers_name", ["admin_headers", "recepcion_headers"])
def test_dashboard_permisos_por_rol(
    client: TestClient, request: pytest.FixtureRequest, headers_name: str
) -> None:
    """El dashboard lo consultan ADMIN y RECEPCION."""
    headers = request.getfixturevalue(headers_name)

    response = client.get("/api/dashboard", headers=headers)

    assert response.status_code == 200


def test_dashboard_requiere_token(client: TestClient) -> None:
    response = client.get("/api/dashboard")

    assert response.status_code == 401
    assert response.json()["code"] == "TOKEN_INVALIDO"
