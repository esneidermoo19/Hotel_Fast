from decimal import Decimal

import pytest
from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from app.models import EstadoReserva
from app.models.enums import MetodoPago, TipoPago
from app.schemas.pago import PagoAnular
from tests.factories import (
    crear_habitacion,
    crear_huesped,
    crear_pago,
    crear_reserva,
    crear_usuario,
)


def pago_payload(**cambios: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "monto": "100000.00",
        "metodo": "EFECTIVO",
        "tipo": "ABONO",
        "referencia": "REF-001",
    }
    payload.update(cambios)
    return payload


def anular_payload(motivo: str = "Pago duplicado") -> dict[str, str]:
    return {"motivoAnulacion": motivo}


def _setup_reserva_con_estado(db, estado: EstadoReserva, sufijo: str = ""):
    usuario = crear_usuario(
        db,
        username=f"user_{estado.value}{sufijo}",
        email=f"user_{estado.value}{sufijo}@example.com",
    )
    habitacion = crear_habitacion(db, numero=800 + hash(f"{estado.value}{sufijo}") % 100)
    huesped = crear_huesped(
        db, numero_documento=f"88888888{hash(f'{estado.value}{sufijo}') % 100:02d}"
    )
    reserva = crear_reserva(
        db,
        huesped=huesped,
        habitacion=habitacion,
        usuario=usuario,
        estado=estado,
        codigo=f"RES-2026-{hash(f'{estado.value}{sufijo}') % 1000000:06d}",
    )
    return usuario, habitacion, huesped, reserva


class TestPagos:
    def test_crear_pago_ok(self, client: TestClient, admin_headers: dict[str, str]) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped, reserva = _setup_reserva_con_estado(
                db, EstadoReserva.CHECK_IN, "_ok"
            )
            reserva_id = reserva.id
        finally:
            db.close()

        response = client.post(
            f"/api/reservas/{reserva_id}/pagos",
            json=pago_payload(),
            headers=admin_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["monto"] == 100000.0
        assert data["metodo"] == "EFECTIVO"
        assert data["tipo"] == "ABONO"
        assert data["referencia"] == "REF-001"
        assert data["anulado"] is False
        assert data["reservaId"] == reserva_id

    def test_crear_pago_valida_monto_cero(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped, reserva = _setup_reserva_con_estado(
                db, EstadoReserva.CHECK_IN, "_val_monto_0"
            )
            reserva_id = reserva.id
        finally:
            db.close()

        response = client.post(
            f"/api/reservas/{reserva_id}/pagos",
            json=pago_payload(monto="0.00"),
            headers=admin_headers,
        )
        assert response.status_code == 422
        assert response.json()["code"] == "VALIDACION"

    def test_crear_pago_valida_monto_negativo(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped, reserva = _setup_reserva_con_estado(
                db, EstadoReserva.CHECK_IN, "_val_monto_neg"
            )
            reserva_id = reserva.id
        finally:
            db.close()

        response = client.post(
            f"/api/reservas/{reserva_id}/pagos",
            json=pago_payload(monto="-100.00"),
            headers=admin_headers,
        )
        assert response.status_code == 422
        assert response.json()["code"] == "VALIDACION"

    def test_crear_pago_reserva_inexistente(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        response = client.post(
            "/api/reservas/999999/pagos",
            json=pago_payload(),
            headers=admin_headers,
        )
        assert response.status_code == 404
        assert response.json()["code"] == "NO_ENCONTRADO"

    @pytest.mark.parametrize(
        "estado",
        [EstadoReserva.CANCELADA, EstadoReserva.NO_SHOW],
    )
    def test_crear_pago_estado_no_permitido(
        self,
        client: TestClient,
        admin_headers: dict[str, str],
        estado: EstadoReserva,
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped, reserva = _setup_reserva_con_estado(
                db, estado, f"_test_{estado.value}"
            )
            reserva_id = reserva.id
        finally:
            db.close()

        response = client.post(
            f"/api/reservas/{reserva_id}/pagos",
            json=pago_payload(),
            headers=admin_headers,
        )
        assert response.status_code == 409
        assert response.json()["code"] == "RESERVA_NO_PERMITE_PAGOS"
        assert estado.value in response.json()["detail"]

    @pytest.mark.parametrize(
        "estado",
        [
            EstadoReserva.PENDIENTE,
            EstadoReserva.CONFIRMADA,
            EstadoReserva.CHECK_IN,
            EstadoReserva.CHECK_OUT,
        ],
    )
    def test_crear_pago_estado_permitido(
        self,
        client: TestClient,
        admin_headers: dict[str, str],
        estado: EstadoReserva,
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped, reserva = _setup_reserva_con_estado(
                db, estado, f"_permitido_{estado.value}"
            )
            reserva_id = reserva.id
        finally:
            db.close()

        response = client.post(
            f"/api/reservas/{reserva_id}/pagos",
            json=pago_payload(),
            headers=admin_headers,
        )
        assert response.status_code == 201

    def test_crear_pago_metodo_invalido(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped, reserva = _setup_reserva_con_estado(
                db, EstadoReserva.CHECK_IN, "_met_invalido"
            )
            reserva_id = reserva.id
        finally:
            db.close()

        response = client.post(
            f"/api/reservas/{reserva_id}/pagos",
            json=pago_payload(metodo="INVALIDO"),
            headers=admin_headers,
        )
        assert response.status_code == 422
        assert response.json()["code"] == "VALIDACION"
        assert "errors" in response.json()

    def test_crear_pago_tipo_invalido(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped, reserva = _setup_reserva_con_estado(
                db, EstadoReserva.CHECK_IN, "_tipo_invalido"
            )
            reserva_id = reserva.id
        finally:
            db.close()

        response = client.post(
            f"/api/reservas/{reserva_id}/pagos",
            json=pago_payload(tipo="INVALIDO"),
            headers=admin_headers,
        )
        assert response.status_code == 422
        assert response.json()["code"] == "VALIDACION"
        assert "errors" in response.json()

    def test_listar_pagos_paginado(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped, reserva = _setup_reserva_con_estado(
                db, EstadoReserva.CHECK_IN, "_listar"
            )
            reserva_id = reserva.id
            for i in range(5):
                crear_pago(
                    db,
                    reserva=reserva,
                    usuario=usuario,
                    monto=Decimal(f"{10000 * (i + 1)}.00"),
                    metodo=MetodoPago.EFECTIVO,
                    tipo=TipoPago.ABONO,
                    referencia=f"REF-{i:03d}",
                )
        finally:
            db.close()

        resp1 = client.get(
            f"/api/reservas/{reserva_id}/pagos",
            params={"pagina": 1, "tamano": 2},
            headers=admin_headers,
        )
        assert resp1.status_code == 200
        p1 = resp1.json()
        assert p1["total"] == 5
        assert p1["pagina"] == 1
        assert p1["tamano"] == 2
        assert len(p1["items"]) == 2

        resp2 = client.get(
            f"/api/reservas/{reserva_id}/pagos",
            params={"pagina": 2, "tamano": 2},
            headers=admin_headers,
        )
        assert resp2.status_code == 200
        p2 = resp2.json()
        assert p2["pagina"] == 2
        assert len(p2["items"]) == 2

        ids_p1 = [item["id"] for item in p1["items"]]
        ids_p2 = [item["id"] for item in p2["items"]]
        assert not set(ids_p1) & set(ids_p2)

    def test_listar_pagos_filtro_solo_vigentes(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped, reserva = _setup_reserva_con_estado(
                db, EstadoReserva.CHECK_IN, "_vigentes"
            )
            reserva_id = reserva.id
            crear_pago(
                db,
                reserva=reserva,
                usuario=usuario,
                monto=Decimal("10000.00"),
                metodo=MetodoPago.EFECTIVO,
                tipo=TipoPago.ABONO,
                referencia="REF-001",
            )
            crear_pago(
                db,
                reserva=reserva,
                usuario=usuario,
                monto=Decimal("20000.00"),
                metodo=MetodoPago.TARJETA,
                tipo=TipoPago.ABONO,
                referencia="REF-002",
                anulado=True,
                motivo_anulacion="Anulado",
            )
        finally:
            db.close()

        resp = client.get(
            f"/api/reservas/{reserva_id}/pagos",
            params={"soloVigentes": "true"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["anulado"] is False
        assert data["items"][0]["referencia"] == "REF-001"

    def test_anular_pago_ok(self, client: TestClient, admin_headers: dict[str, str]) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped, reserva = _setup_reserva_con_estado(
                db, EstadoReserva.CHECK_IN, "_anular_ok"
            )
            reserva_id = reserva.id
            pago = crear_pago(
                db,
                reserva=reserva,
                usuario=usuario,
                monto=Decimal("50000.00"),
                metodo=MetodoPago.EFECTIVO,
                tipo=TipoPago.ABONO,
                referencia="REF-001",
            )
            pago_id = pago.id
        finally:
            db.close()

        response = client.post(
            f"/api/reservas/{reserva_id}/pagos/{pago_id}/anular",
            json=anular_payload("Pago duplicado"),
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["anulado"] is True
        assert data["anuladoPor"] is not None
        assert data["anuladoEn"] is not None
        assert data["motivoAnulacion"] == "Pago duplicado"

    def test_anular_pago_dos_veces_conflicto(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped, reserva = _setup_reserva_con_estado(
                db, EstadoReserva.CHECK_IN, "_anular_2x"
            )
            reserva_id = reserva.id
            pago = crear_pago(
                db,
                reserva=reserva,
                usuario=usuario,
                monto=Decimal("50000.00"),
                metodo=MetodoPago.EFECTIVO,
                tipo=TipoPago.ABONO,
                referencia="REF-001",
            )
            pago_id = pago.id
            from app.services import pago_service
            pago_service.anular_pago(
                db, reserva_id, pago_id, PagoAnular(motivo_anulacion="Primera"), usuario.id
            )
        finally:
            db.close()

        response = client.post(
            f"/api/reservas/{reserva_id}/pagos/{pago_id}/anular",
            json=anular_payload("Segunda vez"),
            headers=admin_headers,
        )
        assert response.status_code == 409
        assert response.json()["code"] == "PAGO_YA_ANULADO"

    def test_anular_pago_otra_reserva_404(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario1, habitacion1, huesped1, reserva1 = _setup_reserva_con_estado(
                db, EstadoReserva.CHECK_IN, "_r1"
            )
            usuario2, habitacion2, huesped2, reserva2 = _setup_reserva_con_estado(
                db, EstadoReserva.CHECK_IN, "_r2"
            )
            pago = crear_pago(
                db,
                reserva=reserva1,
                usuario=usuario1,
                monto=Decimal("10000.00"),
                metodo=MetodoPago.EFECTIVO,
                tipo=TipoPago.ABONO,
                referencia="REF-001",
            )
            pago_id = pago.id
            reserva2_id = reserva2.id
        finally:
            db.close()

        response = client.post(
            f"/api/reservas/{reserva2_id}/pagos/{pago_id}/anular",
            json=anular_payload("Intento anular pago de otra reserva"),
            headers=admin_headers,
        )
        assert response.status_code == 404
        assert response.json()["code"] == "NO_ENCONTRADO"

    def test_anular_pago_inexistente_404(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped, reserva = _setup_reserva_con_estado(
                db, EstadoReserva.CHECK_IN, "_inexistente"
            )
            reserva_id = reserva.id
        finally:
            db.close()

        response = client.post(
            f"/api/reservas/{reserva_id}/pagos/999999/anular",
            json=anular_payload("Pago inexistente"),
            headers=admin_headers,
        )
        assert response.status_code == 404
        assert response.json()["code"] == "NO_ENCONTRADO"

    def test_recepcion_puede_crear_y_listar(
        self,
        client: TestClient,
        admin_headers: dict[str, str],
        recepcion_headers: dict[str, str],
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped, reserva = _setup_reserva_con_estado(
                db, EstadoReserva.CHECK_IN, "_recepcion"
            )
            reserva_id = reserva.id
        finally:
            db.close()

        creado = client.post(
            f"/api/reservas/{reserva_id}/pagos",
            json=pago_payload(),
            headers=recepcion_headers,
        )
        assert creado.status_code == 201

        listado = client.get(
            f"/api/reservas/{reserva_id}/pagos", headers=recepcion_headers
        )
        assert listado.status_code == 200

    def test_anular_requiere_admin(
        self,
        client: TestClient,
        admin_headers: dict[str, str],
        recepcion_headers: dict[str, str],
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped, reserva = _setup_reserva_con_estado(
                db, EstadoReserva.CHECK_IN, "_anular_admin"
            )
            reserva_id = reserva.id
            pago = crear_pago(
                db,
                reserva=reserva,
                usuario=usuario,
                monto=Decimal("50000.00"),
                metodo=MetodoPago.EFECTIVO,
                tipo=TipoPago.ABONO,
                referencia="REF-001",
            )
            pago_id = pago.id
        finally:
            db.close()

        response = client.post(
            f"/api/reservas/{reserva_id}/pagos/{pago_id}/anular",
            json=anular_payload("Intento recepcion"),
            headers=recepcion_headers,
        )
        assert response.status_code == 403

    def test_rutas_requieren_token(self, client: TestClient) -> None:
        response = client.get("/api/reservas/1/pagos")
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"