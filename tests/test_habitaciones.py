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


# --- Listado con filtros -------------------------------------------------------


def test_listar_sin_filtros_sigue_devolviendo_todas_las_habitaciones(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    """El GET sin filtros devuelve todas, con el formato de antes y el campo limpieza."""
    numeros = [701, 702, 703]
    creadas = [
        client.post(
            "/api/habitaciones",
            json=habitacion_payload(numero),
            headers=admin_headers,
        )
        for numero in numeros
    ]
    assert [respuesta.status_code for respuesta in creadas] == [201, 201, 201]

    response = client.get("/api/habitaciones", headers=admin_headers)

    assert response.status_code == 200
    datos = response.json()
    assert [item["numero"] for item in datos] == numeros

    campos_antes = {
        "id",
        "numero",
        "tipo",
        "capacidad",
        "precioPorNoche",
        "estado",
        "descripcion",
        "createdAt",
        "updatedAt",
    }
    for item in datos:
        assert set(item) == campos_antes | {"limpieza"}
        assert item["limpieza"] in {"LIMPIA", "SUCIA"}
        assert isinstance(item["precioPorNoche"], float)


def test_filtros_de_habitaciones(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    doble = client.post(
        "/api/habitaciones", json=habitacion_payload(711, tipo="DOBLE"), headers=admin_headers
    ).json()
    suite = client.post(
        "/api/habitaciones",
        json=habitacion_payload(712, tipo="SUITE", estado="OCUPADA"),
        headers=admin_headers,
    ).json()
    client.patch(
        f"/api/habitaciones/{suite['id']}/limpieza",
        json={"limpieza": "SUCIA"},
        headers=admin_headers,
    )
    simple = client.post(
        "/api/habitaciones",
        json=habitacion_payload(713, tipo="SIMPLE", estado="MANTENIMIENTO"),
        headers=admin_headers,
    ).json()

    def ids(params: dict[str, str]) -> list[int]:
        respuesta = client.get("/api/habitaciones", params=params, headers=admin_headers)
        assert respuesta.status_code == 200
        return [item["id"] for item in respuesta.json()]

    assert ids({}) == [doble["id"], suite["id"], simple["id"]]
    assert ids({"estado": "OCUPADA"}) == [suite["id"]]
    assert ids({"estado": "MANTENIMIENTO"}) == [simple["id"]]
    assert ids({"tipo": "SUITE"}) == [suite["id"]]
    assert ids({"limpieza": "SUCIA"}) == [suite["id"]]
    assert ids({"limpieza": "LIMPIA"}) == [doble["id"], simple["id"]]
    assert ids({"tipo": "DOBLE", "limpieza": "LIMPIA"}) == [doble["id"]]


@pytest.mark.parametrize(
    "params",
    [
        {"estado": "OTRO"},
        {"tipo": "OTRO"},
        {"limpieza": "OTRO"},
    ],
)
def test_filtro_invalido_devuelve_422(
    client: TestClient,
    admin_headers: dict[str, str],
    params: dict[str, str],
) -> None:
    response = client.get("/api/habitaciones", params=params, headers=admin_headers)

    assert response.status_code == 422


# --- Limpieza ------------------------------------------------------------------


def test_limpieza_cambia_el_estado_y_se_audita(
    client: TestClient,
    admin_headers: dict[str, str],
    recepcion_headers: dict[str, str],
    recepcion_user,
) -> None:
    creado = client.post(
        "/api/habitaciones", json=habitacion_payload(721), headers=admin_headers
    ).json()
    assert creado["limpieza"] == "LIMPIA"

    sucia = client.patch(
        f"/api/habitaciones/{creado['id']}/limpieza",
        json={"limpieza": "SUCIA"},
        headers=recepcion_headers,
    )
    assert sucia.status_code == 200
    assert sucia.json()["limpieza"] == "SUCIA"

    limpia = client.patch(
        f"/api/habitaciones/{creado['id']}/limpieza",
        json={"limpieza": "LIMPIA"},
        headers=recepcion_headers,
    )
    assert limpia.status_code == 200
    assert limpia.json()["limpieza"] == "LIMPIA"

    auditoria = client.get(
        "/api/auditoria",
        params={"entidad": "Habitacion", "accion": "LIMPIEZA"},
        headers=admin_headers,
    )
    assert auditoria.status_code == 200
    assert auditoria.json()["total"] == 2

    # El listado va del más reciente al más antiguo.
    detalle = auditoria.json()["items"][0]["detalle"]
    assert auditoria.json()["items"][0]["usuarioId"] == recepcion_user.id
    assert detalle["limpieza_anterior"] == "SUCIA"
    assert detalle["limpieza_nueva"] == "LIMPIA"

    detalle = auditoria.json()["items"][1]["detalle"]
    assert detalle["limpieza_anterior"] == "LIMPIA"
    assert detalle["limpieza_nueva"] == "SUCIA"


def test_limpieza_se_permite_con_habitacion_ocupada(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    creado = client.post(
        "/api/habitaciones",
        json=habitacion_payload(731, estado="OCUPADA"),
        headers=admin_headers,
    ).json()

    response = client.patch(
        f"/api/habitaciones/{creado['id']}/limpieza",
        json={"limpieza": "SUCIA"},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["estado"] == "OCUPADA"
    assert response.json()["limpieza"] == "SUCIA"


def test_limpieza_habitacion_inexistente_devuelve_404(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.patch(
        "/api/habitaciones/9999/limpieza",
        json={"limpieza": "SUCIA"},
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert isinstance(response.json()["detail"], str)


def test_limpieza_valor_invalido_devuelve_422(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    creado = client.post(
        "/api/habitaciones", json=habitacion_payload(741), headers=admin_headers
    ).json()

    response = client.patch(
        f"/api/habitaciones/{creado['id']}/limpieza",
        json={"limpieza": "GARABATO"},
        headers=admin_headers,
    )

    assert response.status_code == 422


def test_limpieza_requiere_token(client: TestClient) -> None:
    response = client.patch(
        "/api/habitaciones/1/limpieza", json={"limpieza": "SUCIA"}
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
