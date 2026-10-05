import pytest
from fastapi.testclient import TestClient

from app.routers.habitaciones import router


def habitacion_payload(numero: int, **cambios: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "numero": numero,
        "tipo": "DOBLE",
        "capacidad": 2,
        "precioPorNoche": 120.50,
        "descripcion": "Habitacion de prueba",
    }
    payload.update(cambios)
    return payload


def test_habitaciones_router_prefix() -> None:
    assert router.prefix == "/api/habitaciones"


def test_crud_completo_habitaciones(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    creado = client.post(
        "/api/habitaciones",
        json=habitacion_payload(101),
        headers=admin_headers,
    )

    assert creado.status_code == 201
    habitacion = creado.json()
    assert habitacion["numero"] == 101
    assert habitacion["estado"] == "DISPONIBLE"
    assert isinstance(habitacion["precioPorNoche"], float)
    habitacion_id = habitacion["id"]

    listado = client.get("/api/habitaciones", headers=admin_headers)
    assert listado.status_code == 200
    assert [item["id"] for item in listado.json()] == [habitacion_id]

    detalle = client.get(
        f"/api/habitaciones/{habitacion_id}",
        headers=admin_headers,
    )
    assert detalle.status_code == 200
    assert detalle.json()["precioPorNoche"] == 120.5

    actualizada = client.put(
        f"/api/habitaciones/{habitacion_id}",
        json=habitacion_payload(101, tipo="SUITE", capacidad=3),
        headers=admin_headers,
    )
    assert actualizada.status_code == 200
    assert actualizada.json()["tipo"] == "SUITE"
    assert actualizada.json()["capacidad"] == 3

    estado = client.patch(
        f"/api/habitaciones/{habitacion_id}/estado",
        json={"estado": "OCUPADA"},
        headers=admin_headers,
    )
    assert estado.status_code == 200
    assert estado.json()["estado"] == "OCUPADA"

    eliminada = client.delete(
        f"/api/habitaciones/{habitacion_id}",
        headers=admin_headers,
    )
    assert eliminada.status_code == 204
    assert eliminada.content == b""
    assert client.get(
        f"/api/habitaciones/{habitacion_id}",
        headers=admin_headers,
    ).status_code == 404


def test_numero_habitacion_duplicado_devuelve_409(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    payload = habitacion_payload(202)
    primera = client.post("/api/habitaciones", json=payload, headers=admin_headers)
    segunda = client.post("/api/habitaciones", json=payload, headers=admin_headers)

    assert primera.status_code == 201
    assert segunda.status_code == 409
    assert "202" in segunda.json()["detail"]


def test_habitacion_inexistente_devuelve_404(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.get("/api/habitaciones/9999", headers=admin_headers)

    assert response.status_code == 404
    assert isinstance(response.json()["detail"], str)


def test_recepcion_puede_consultar_y_cambiar_estado(
    client,
    admin_headers: dict[str, str],
    recepcion_headers: dict[str, str],
) -> None:
    creado = client.post(
        "/api/habitaciones",
        json=habitacion_payload(303),
        headers=admin_headers,
    )
    habitacion_id = creado.json()["id"]

    listado = client.get("/api/habitaciones", headers=recepcion_headers)
    estado = client.patch(
        f"/api/habitaciones/{habitacion_id}/estado",
        json={"estado": "MANTENIMIENTO"},
        headers=recepcion_headers,
    )

    assert listado.status_code == 200
    assert estado.status_code == 200
    assert estado.json()["estado"] == "MANTENIMIENTO"


def test_recepcion_no_puede_crear_actualizar_ni_eliminar(
    client,
    admin_headers: dict[str, str],
    recepcion_headers: dict[str, str],
) -> None:
    creado = client.post(
        "/api/habitaciones",
        json=habitacion_payload(404),
        headers=admin_headers,
    )
    habitacion_id = creado.json()["id"]

    crear = client.post(
        "/api/habitaciones",
        json=habitacion_payload(405),
        headers=recepcion_headers,
    )
    actualizar = client.put(
        f"/api/habitaciones/{habitacion_id}",
        json=habitacion_payload(404, capacidad=4),
        headers=recepcion_headers,
    )
    eliminar = client.delete(
        f"/api/habitaciones/{habitacion_id}",
        headers=recepcion_headers,
    )

    assert crear.status_code == 403
    assert actualizar.status_code == 403
    assert eliminar.status_code == 403


@pytest.mark.parametrize(
    "cambios",
    [
        {"precioPorNoche": 0},
        {"capacidad": 0},
        {"tipo": "TRIPLE"},
    ],
)
def test_validacion_de_habitacion_devuelve_422(
    client: TestClient,
    admin_headers: dict[str, str],
    cambios: dict[str, object],
) -> None:
    response = client.post(
        "/api/habitaciones",
        json=habitacion_payload(505, **cambios),
        headers=admin_headers,
    )

    assert response.status_code == 422


def test_rutas_requieren_token(client: TestClient) -> None:
    response = client.get("/api/habitaciones")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
