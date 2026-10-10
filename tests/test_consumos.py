from decimal import Decimal

import pytest
from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from app.models import EstadoReserva
from app.schemas.consumo import ConsumoAnular
from tests.factories import (
    crear_consumo,
    crear_habitacion,
    crear_huesped,
    crear_reserva,
    crear_usuario,
)


def consumo_payload(**cambios: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "descripcion": "Minibar",
        "cantidad": 2,
        "precioUnitario": "25000.00",
    }
    payload.update(cambios)
    return payload


def anular_payload(motivo: str = "Error de registro") -> dict[str, str]:
    return {"motivoAnulacion": motivo}


_CONTADOR = 0


def _siguiente() -> int:
    global _CONTADOR
    _CONTADOR += 1
    return _CONTADOR


def _setup_reserva_con_estado(db, estado: EstadoReserva, sufijo: str = ""):
    # Secuencia determinista y unica (evita colisiones UNIQUE; hash() es
    # aleatorio por proceso y hacia fallar este setup de forma intermitente).
    secuencia = _siguiente()
    usuario = crear_usuario(
        db,
        username=f"user_{estado.value}{sufijo}_{secuencia}",
        email=f"user_{estado.value}{sufijo}_{secuencia}@example.com",
    )
    habitacion = crear_habitacion(db, numero=900 + secuencia)
    huesped = crear_huesped(
        db, numero_documento=f"99999999{secuencia:02d}"
    )
    reserva = crear_reserva(
        db,
        huesped=huesped,
        habitacion=habitacion,
        usuario=usuario,
        estado=estado,
        codigo=f"RES-2026-{secuencia:06d}",
    )
    return usuario, habitacion, huesped, reserva


class TestConsumos:
    def test_crear_consumo_ok(self, client: TestClient, admin_headers: dict[str, str]) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped, reserva = _setup_reserva_con_estado(
                db, EstadoReserva.CHECK_IN, "_ok"
            )
            reserva_id = reserva.id
        finally:
            db.close()

        response = client.post(
            f"/api/reservas/{reserva_id}/consumos",
            json=consumo_payload(),
            headers=admin_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["descripcion"] == "Minibar"
        assert data["cantidad"] == 2
        assert data["precioUnitario"] == 25000.0
        assert data["total"] == 50000.0
        assert data["anulado"] is False
        assert data["reservaId"] == reserva_id

    def test_crear_consumo_valida_cantidad_cero(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped, reserva = _setup_reserva_con_estado(
                db, EstadoReserva.CHECK_IN, "_val_cant_0"
            )
            reserva_id = reserva.id
        finally:
            db.close()

        response = client.post(
            f"/api/reservas/{reserva_id}/consumos",
            json=consumo_payload(cantidad=0),
            headers=admin_headers,
        )
        assert response.status_code == 422
        assert response.json()["code"] == "VALIDACION"

    def test_crear_consumo_valida_cantidad_negativa(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped, reserva = _setup_reserva_con_estado(
                db, EstadoReserva.CHECK_IN, "_val_cant_neg"
            )
            reserva_id = reserva.id
        finally:
            db.close()

        response = client.post(
            f"/api/reservas/{reserva_id}/consumos",
            json=consumo_payload(cantidad=-1),
            headers=admin_headers,
        )
        assert response.status_code == 422
        assert response.json()["code"] == "VALIDACION"

    def test_crear_consumo_valida_precio_cero(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped, reserva = _setup_reserva_con_estado(
                db, EstadoReserva.CHECK_IN, "_val_precio_0"
            )
            reserva_id = reserva.id
        finally:
            db.close()

        response = client.post(
            f"/api/reservas/{reserva_id}/consumos",
            json=consumo_payload(precioUnitario="0.00"),
            headers=admin_headers,
        )
        assert response.status_code == 422
        assert response.json()["code"] == "VALIDACION"

    def test_crear_consumo_valida_precio_negativo(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped, reserva = _setup_reserva_con_estado(
                db, EstadoReserva.CHECK_IN, "_val_precio_neg"
            )
            reserva_id = reserva.id
        finally:
            db.close()

        response = client.post(
            f"/api/reservas/{reserva_id}/consumos",
            json=consumo_payload(precioUnitario="-10.00"),
            headers=admin_headers,
        )
        assert response.status_code == 422
        assert response.json()["code"] == "VALIDACION"

    def test_crear_consumo_reserva_inexistente(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        response = client.post(
            "/api/reservas/999999/consumos",
            json=consumo_payload(),
            headers=admin_headers,
        )
        assert response.status_code == 404
        assert response.json()["code"] == "NO_ENCONTRADO"

    @pytest.mark.parametrize(
        "estado",
        [
            EstadoReserva.PENDIENTE,
            EstadoReserva.CONFIRMADA,
            EstadoReserva.CHECK_OUT,
            EstadoReserva.CANCELADA,
            EstadoReserva.NO_SHOW,
        ],
    )
    def test_crear_consumo_estado_no_permitido(
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
            f"/api/reservas/{reserva_id}/consumos",
            json=consumo_payload(),
            headers=admin_headers,
        )
        assert response.status_code == 409
        assert response.json()["code"] == "RESERVA_NO_PERMITE_CARGOS"
        assert estado.value in response.json()["detail"]

    def test_listar_consumos_paginado(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped, reserva = _setup_reserva_con_estado(
                db, EstadoReserva.CHECK_IN, "_listar"
            )
            reserva_id = reserva.id
            for i in range(5):
                crear_consumo(
                    db,
                    reserva=reserva,
                    usuario=usuario,
                    descripcion=f"Consumo {i}",
                    cantidad=1,
                    precio_unitario=Decimal("10000.00"),
                )
        finally:
            db.close()

        resp1 = client.get(
            f"/api/reservas/{reserva_id}/consumos",
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
            f"/api/reservas/{reserva_id}/consumos",
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

    def test_listar_consumos_filtro_solo_vigentes(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped, reserva = _setup_reserva_con_estado(
                db, EstadoReserva.CHECK_IN, "_vigentes"
            )
            reserva_id = reserva.id
            crear_consumo(
                db,
                reserva=reserva,
                usuario=usuario,
                descripcion="Vigente",
                cantidad=1,
                precio_unitario=Decimal("10000.00"),
            )
            crear_consumo(
                db,
                reserva=reserva,
                usuario=usuario,
                descripcion="Anulado",
                cantidad=1,
                precio_unitario=Decimal("20000.00"),
                anulado=True,
            )
        finally:
            db.close()

        resp = client.get(
            f"/api/reservas/{reserva_id}/consumos",
            params={"soloVigentes": "true"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["anulado"] is False
        assert data["items"][0]["descripcion"] == "Vigente"

    def test_anular_consumo_ok(self, client: TestClient, admin_headers: dict[str, str]) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped, reserva = _setup_reserva_con_estado(
                db, EstadoReserva.CHECK_IN, "_anular_ok"
            )
            reserva_id = reserva.id
            consumo = crear_consumo(
                db,
                reserva=reserva,
                usuario=usuario,
                descripcion="Para anular",
                cantidad=1,
                precio_unitario=Decimal("15000.00"),
            )
            consumo_id = consumo.id
        finally:
            db.close()

        response = client.post(
            f"/api/reservas/{reserva_id}/consumos/{consumo_id}/anular",
            json=anular_payload("Error en registro"),
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["anulado"] is True
        assert data["anuladoPor"] is not None
        assert data["anuladoEn"] is not None
        assert data["motivoAnulacion"] == "Error en registro"

    def test_anular_consumo_dos_veces_conflicto(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        db = TestingSessionLocal()
        try:
            usuario, habitacion, huesped, reserva = _setup_reserva_con_estado(
                db, EstadoReserva.CHECK_IN, "_anular_2x"
            )
            reserva_id = reserva.id
            consumo = crear_consumo(
                db,
                reserva=reserva,
                usuario=usuario,
                descripcion="Para anular dos veces",
                cantidad=1,
                precio_unitario=Decimal("15000.00"),
            )
            consumo_id = consumo.id
            from app.services import consumo_service
            consumo_service.anular_consumo(
                db, reserva_id, consumo_id, ConsumoAnular(motivo_anulacion="Primera"), usuario.id
            )
        finally:
            db.close()

        response = client.post(
            f"/api/reservas/{reserva_id}/consumos/{consumo_id}/anular",
            json=anular_payload("Segunda vez"),
            headers=admin_headers,
        )
        assert response.status_code == 409
        assert response.json()["code"] == "CONSUMO_YA_ANULADO"

    def test_anular_consumo_otra_reserva_404(
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
            consumo = crear_consumo(
                db,
                reserva=reserva1,
                usuario=usuario1,
                descripcion="Consumo reserva 1",
                cantidad=1,
                precio_unitario=Decimal("10000.00"),
            )
            consumo_id = consumo.id
            reserva2_id = reserva2.id
        finally:
            db.close()

        response = client.post(
            f"/api/reservas/{reserva2_id}/consumos/{consumo_id}/anular",
            json=anular_payload("Intento anular consumo de otra reserva"),
            headers=admin_headers,
        )
        assert response.status_code == 404
        assert response.json()["code"] == "NO_ENCONTRADO"

    def test_anular_consumo_inexistente_404(
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
            f"/api/reservas/{reserva_id}/consumos/999999/anular",
            json=anular_payload("Consumo inexistente"),
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
            f"/api/reservas/{reserva_id}/consumos",
            json=consumo_payload(),
            headers=recepcion_headers,
        )
        assert creado.status_code == 201

        listado = client.get(
            f"/api/reservas/{reserva_id}/consumos", headers=recepcion_headers
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
            consumo = crear_consumo(
                db,
                reserva=reserva,
                usuario=usuario,
                descripcion="Para anular",
                cantidad=1,
                precio_unitario=Decimal("15000.00"),
            )
            consumo_id = consumo.id
        finally:
            db.close()

        response = client.post(
            f"/api/reservas/{reserva_id}/consumos/{consumo_id}/anular",
            json=anular_payload("Intento recepcion"),
            headers=recepcion_headers,
        )
        assert response.status_code == 403

    def test_rutas_requieren_token(self, client: TestClient) -> None:
        response = client.get("/api/reservas/1/consumos")
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"