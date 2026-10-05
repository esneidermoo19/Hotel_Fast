from datetime import date
from decimal import Decimal

from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from tests.factories import (
    crear_consumo,
    crear_habitacion,
    crear_huesped,
    crear_pago,
    crear_reserva,
    crear_usuario,
)


def _setup_basico(db):
    usuario = crear_usuario(db, username="test_user", email="test@example.com")
    habitacion = crear_habitacion(db, numero=201)
    huesped = crear_huesped(db, numero_documento="87654321")
    return usuario, habitacion, huesped


class TestCuentas:
    def test_cuenta_reserva_sin_movimientos(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped = _setup_basico(db)
            reserva = crear_reserva(
                db,
                huesped=huesped,
                habitacion=habitacion,
                usuario=usuario,
                codigo="RES-2026-001",
                fecha_entrada=date(2026, 10, 15),
                fecha_salida=date(2026, 10, 18),  # 3 noches
                precio_noche_aplicado=Decimal("150000.00"),
                total_estimado=Decimal("450000.00"),
            )
            reserva_id = reserva.id
        finally:
            db.close()

        response = client.get(
            f"/api/cuentas/{reserva_id}",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["totalAlojamiento"] == 450000.0  # 3 x 150000
        assert data["totalConsumosVigentes"] == 0.0
        assert data["totalPagosVigentes"] == 0.0
        assert data["saldoPendiente"] == 450000.0
        assert data["detalleConsumos"] == []
        assert data["detallePagos"] == []

    def test_cuenta_con_consumos_y_pagos(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped = _setup_basico(db)
            reserva = crear_reserva(
                db,
                huesped=huesped,
                habitacion=habitacion,
                usuario=usuario,
                codigo="RES-2026-002",
                fecha_entrada=date(2026, 10, 15),
                fecha_salida=date(2026, 10, 18),  # 3 noches
                precio_noche_aplicado=Decimal("150000.00"),
                total_estimado=Decimal("450000.00"),
            )
            reserva_id = reserva.id
            # 2 consumos vigentes
            crear_consumo(
                db,
                reserva=reserva,
                usuario=usuario,
                descripcion="Minibar",
                cantidad=2,
                precio_unitario=Decimal("25000.00"),
            )
            crear_consumo(
                db,
                reserva=reserva,
                usuario=usuario,
                descripcion="Lavanderia",
                cantidad=1,
                precio_unitario=Decimal("30000.00"),
            )
            # 1 pago vigente
            crear_pago(
                db,
                reserva=reserva,
                usuario=usuario,
                monto=Decimal("100000.00"),
                metodo="EFECTIVO",
                tipo="ABONO",
            )
        finally:
            db.close()

        response = client.get(
            f"/api/cuentas/{reserva_id}",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["totalAlojamiento"] == 450000.0  # 3 x 150000
        assert data["totalConsumosVigentes"] == 80000.0  # 2*25000 + 1*30000
        assert data["totalPagosVigentes"] == 100000.0
        assert data["saldoPendiente"] == 430000.0  # 450000 + 80000 - 100000
        assert len(data["detalleConsumos"]) == 2
        assert len(data["detallePagos"]) == 1

    def test_cuenta_con_anulados_no_suman(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped = _setup_basico(db)
            reserva = crear_reserva(
                db,
                huesped=huesped,
                habitacion=habitacion,
                usuario=usuario,
                codigo="RES-2026-003",
                fecha_entrada=date(2026, 10, 15),
                fecha_salida=date(2026, 10, 18),  # 3 noches
                precio_noche_aplicado=Decimal("150000.00"),
                total_estimado=Decimal("450000.00"),
            )
            reserva_id = reserva.id
            # 1 consumo vigente, 1 anulado
            crear_consumo(
                db,
                reserva=reserva,
                usuario=usuario,
                descripcion="Vigente",
                cantidad=1,
                precio_unitario=Decimal("20000.00"),
                anulado=False,
            )
            crear_consumo(
                db,
                reserva=reserva,
                usuario=usuario,
                descripcion="Anulado",
                cantidad=1,
                precio_unitario=Decimal("50000.00"),
                anulado=True,
            )
            # 1 pago vigente, 1 anulado
            crear_pago(
                db,
                reserva=reserva,
                usuario=usuario,
                monto=Decimal("100000.00"),
                metodo="EFECTIVO",
                tipo="ABONO",
                anulado=False,
            )
            crear_pago(
                db,
                reserva=reserva,
                usuario=usuario,
                monto=Decimal("50000.00"),
                metodo="TARJETA",
                tipo="ABONO",
                anulado=True,
            )
        finally:
            db.close()

        response = client.get(
            f"/api/cuentas/{reserva_id}",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["totalAlojamiento"] == 450000.0
        assert data["totalConsumosVigentes"] == 20000.0  # solo el vigente
        assert data["totalPagosVigentes"] == 100000.0  # solo el vigente
        assert data["saldoPendiente"] == 370000.0  # 450000 + 20000 - 100000
        # Detalle incluye todos (4 items)
        assert len(data["detalleConsumos"]) == 2
        assert len(data["detallePagos"]) == 2
        # Verificar que anulados están en el detalle con anulado=true
        consumos_anulados = [c for c in data["detalleConsumos"] if c["anulado"]]
        assert len(consumos_anulados) == 1
        pagos_anulados = [p for p in data["detallePagos"] if p["anulado"]]
        assert len(pagos_anulados) == 1

    def test_cuenta_saldo_negativo_por_sobrepago(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped = _setup_basico(db)
            reserva = crear_reserva(
                db,
                huesped=huesped,
                habitacion=habitacion,
                usuario=usuario,
                codigo="RES-2026-004",
                fecha_entrada=date(2026, 10, 15),
                fecha_salida=date(2026, 10, 18),  # 3 noches
                precio_noche_aplicado=Decimal("150000.00"),
                total_estimado=Decimal("450000.00"),
            )
            reserva_id = reserva.id
            # Pagos que superan el alojamiento
            crear_pago(
                db,
                reserva=reserva,
                usuario=usuario,
                monto=Decimal("500000.00"),
                metodo="EFECTIVO",
                tipo="PAGO_FINAL",
            )
        finally:
            db.close()

        response = client.get(
            f"/api/cuentas/{reserva_id}",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["totalAlojamiento"] == 450000.0
        assert data["totalConsumosVigentes"] == 0.0
        assert data["totalPagosVigentes"] == 500000.0
        assert data["saldoPendiente"] == -50000.0  # 450000 - 500000

    def test_cuenta_reserva_inexistente(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        response = client.get(
            "/api/cuentas/999999",
            headers=admin_headers,
        )
        assert response.status_code == 404
        assert response.json()["code"] == "NO_ENCONTRADO"

    def test_cuenta_usa_precio_noche_aplicado_no_total_estimado(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        """Si precio_noche_aplicado x noches difiere de total_estimado,
        la cuenta usa precio_noche_aplicado x noches."""
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped = _setup_basico(db)
            # 3 noches, precio_noche = 100000, pero total_estimado = 500000 (diferente)
            reserva = crear_reserva(
                db,
                huesped=huesped,
                habitacion=habitacion,
                usuario=usuario,
                codigo="RES-2026-005",
                fecha_entrada=date(2026, 10, 15),
                fecha_salida=date(2026, 10, 18),  # 3 noches
                precio_noche_aplicado=Decimal("100000.00"),
                total_estimado=Decimal("500000.00"),  # intencionalmente distinto
            )
            reserva_id = reserva.id
        finally:
            db.close()

        response = client.get(
            f"/api/cuentas/{reserva_id}",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        # Debe usar 3 * 100000 = 300000, NO total_estimado (500000)
        assert data["totalAlojamiento"] == 300000.0
        assert data["saldoPendiente"] == 300000.0

    def test_cuenta_cero_noches(self) -> None:
        """Reserva con salida = entrada => 0 noches, alojamiento = 0 sin error.
        
        Prueba unitaria directa del cálculo (el modelo tiene constraint
        fecha_salida > fecha_entrada que impide crear tal reserva en BD).
        """
        from unittest.mock import MagicMock

        from app.models import Reserva
        from app.services.cuenta_service import calcular_cuenta
        
        # Mock reserva con 0 noches
        reserva_mock = MagicMock(spec=Reserva)
        reserva_mock.fecha_entrada = date(2026, 10, 15)
        reserva_mock.fecha_salida = date(2026, 10, 15)  # misma fecha = 0 noches
        reserva_mock.precio_noche_aplicado = Decimal("150000.00")
        
        db_mock = MagicMock()
        db_mock.get.return_value = reserva_mock
        db_mock.scalars.return_value.all.return_value = []  # sin consumos ni pagos
        
        cuenta = calcular_cuenta(db_mock, 1)
        assert cuenta.total_alojamiento == Decimal("0.00")
        assert cuenta.total_consumos_vigentes == Decimal("0.00")
        assert cuenta.total_pagos_vigentes == Decimal("0.00")
        assert cuenta.saldo_pendiente == Decimal("0.00")

    def test_calcular_noches(self) -> None:
        """Pruebas unitarias puras de _calcular_noches sin mocks de BD."""
        from app.services.cuenta_service import _calcular_noches
        
        # Mismo día = 0 noches
        assert _calcular_noches(date(2026, 10, 15), date(2026, 10, 15)) == 0
        # Salida anterior a entrada = 0 noches
        assert _calcular_noches(date(2026, 10, 15), date(2026, 10, 14)) == 0
        # 3 noches
        assert _calcular_noches(date(2026, 10, 15), date(2026, 10, 18)) == 3
        # 1 noche
        assert _calcular_noches(date(2026, 10, 15), date(2026, 10, 16)) == 1
        # 7 noches (una semana)
        assert _calcular_noches(date(2026, 10, 15), date(2026, 10, 22)) == 7

    def test_cuenta_reembolso_resta(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        """Pagos con tipo REEMBOLSO se restan (son devoluciones)."""
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped = _setup_basico(db)
            reserva = crear_reserva(
                db,
                huesped=huesped,
                habitacion=habitacion,
                usuario=usuario,
                codigo="RES-2026-007",
                fecha_entrada=date(2026, 10, 15),
                fecha_salida=date(2026, 10, 18),  # 3 noches
                precio_noche_aplicado=Decimal("150000.00"),
                total_estimado=Decimal("450000.00"),
            )
            reserva_id = reserva.id
            # Pago normal
            crear_pago(
                db,
                reserva=reserva,
                usuario=usuario,
                monto=Decimal("200000.00"),
                metodo="EFECTIVO",
                tipo="ABONO",
            )
            # Reembolso (devolución)
            crear_pago(
                db,
                reserva=reserva,
                usuario=usuario,
                monto=Decimal("50000.00"),
                metodo="EFECTIVO",
                tipo="REEMBOLSO",
            )
        finally:
            db.close()

        response = client.get(
            f"/api/cuentas/{reserva_id}",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        # totalPagosVigentes = 200000 - 50000 = 150000
        assert data["totalPagosVigentes"] == 150000.0
        assert data["saldoPendiente"] == 300000.0  # 450000 + 0 - 150000

    def test_cuenta_permisos_admin_y_recepcion(
        self,
        client: TestClient,
        admin_headers: dict[str, str],
        recepcion_headers: dict[str, str],
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped = _setup_basico(db)
            reserva = crear_reserva(
                db,
                huesped=huesped,
                habitacion=habitacion,
                usuario=usuario,
                codigo="RES-2026-008",
                fecha_entrada=date(2026, 10, 15),
                fecha_salida=date(2026, 10, 18),
                precio_noche_aplicado=Decimal("150000.00"),
                total_estimado=Decimal("450000.00"),
            )
            reserva_id = reserva.id
        finally:
            db.close()

        # ADMIN puede
        resp_admin = client.get(f"/api/cuentas/{reserva_id}", headers=admin_headers)
        assert resp_admin.status_code == 200

        # RECEPCION puede
        resp_recepcion = client.get(f"/api/cuentas/{reserva_id}", headers=recepcion_headers)
        assert resp_recepcion.status_code == 200

    def test_cuenta_sin_token(self, client: TestClient) -> None:
        response = client.get("/api/cuentas/1")
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"