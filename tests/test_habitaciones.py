import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
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
        "imagenes",
        "imagenPrincipalUrl",
    }
    for item in datos:
        assert set(item) == campos_antes | {"limpieza"}
        assert item["limpieza"] in {"LIMPIA", "SUCIA"}
        assert item["imagenes"] == []
        assert item["imagenPrincipalUrl"] is None
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


# --- Imagenes de habitaciones -------------------------------------------------


FIRMA_PNG = b"\x89PNG\r\n\x1a\n"


@pytest.fixture
def media_dir(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "media_dir", str(tmp_path))
    return tmp_path


def _crear_habitacion(
    client: TestClient,
    headers: dict[str, str],
    numero: int,
) -> int:
    respuesta = client.post(
        "/api/habitaciones",
        json=habitacion_payload(numero),
        headers=headers,
    )
    assert respuesta.status_code == 201
    return respuesta.json()["id"]


def _subir_imagen(
    client: TestClient,
    headers: dict[str, str],
    habitacion_id: int,
    nombre: str,
    contenido: bytes = FIRMA_PNG + b"contenido",
) -> dict:
    respuesta = client.post(
        f"/api/habitaciones/{habitacion_id}/imagenes",
        files={"archivo": (nombre, contenido, "image/png")},
        headers=headers,
    )
    assert respuesta.status_code == 201
    return respuesta.json()


def test_subir_imagen_valida(
    client: TestClient,
    admin_headers: dict[str, str],
    media_dir,
) -> None:
    habitacion_id = _crear_habitacion(client, admin_headers, 901)

    imagen = _subir_imagen(client, admin_headers, habitacion_id, "foto.png")

    assert imagen["esPrincipal"] is True
    assert imagen["orden"] == 1
    assert imagen["url"].startswith("/media/")
    assert imagen["url"].endswith(".png")
    assert (media_dir / imagen["url"].split("/")[-1]).exists()


def test_subir_imagen_tipo_invalido(
    client: TestClient,
    admin_headers: dict[str, str],
    media_dir,
) -> None:
    habitacion_id = _crear_habitacion(client, admin_headers, 902)

    respuesta = client.post(
        f"/api/habitaciones/{habitacion_id}/imagenes",
        files={"archivo": ("foto.gif", b"GIF89a\x01\x00\x01\x00", "image/gif")},
        headers=admin_headers,
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["code"] == "FORMATO_IMAGEN_INVALIDO"


def test_subir_imagen_png_con_contenido_falso(
    client: TestClient,
    admin_headers: dict[str, str],
    media_dir,
) -> None:
    habitacion_id = _crear_habitacion(client, admin_headers, 903)

    respuesta = client.post(
        f"/api/habitaciones/{habitacion_id}/imagenes",
        files={"archivo": ("foto.png", b"esto no es una imagen", "image/png")},
        headers=admin_headers,
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["code"] == "FORMATO_IMAGEN_INVALIDO"


def test_subir_imagen_demasiado_grande(
    client: TestClient,
    admin_headers: dict[str, str],
    media_dir,
) -> None:
    habitacion_id = _crear_habitacion(client, admin_headers, 904)
    contenido = FIRMA_PNG + b"0" * (5 * 1024 * 1024)

    respuesta = client.post(
        f"/api/habitaciones/{habitacion_id}/imagenes",
        files={"archivo": ("foto.png", contenido, "image/png")},
        headers=admin_headers,
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["code"] == "IMAGEN_MUY_GRANDE"


def test_subir_imagen_sin_permiso(
    client: TestClient,
    admin_headers: dict[str, str],
    recepcion_headers: dict[str, str],
    media_dir,
) -> None:
    habitacion_id = _crear_habitacion(client, admin_headers, 905)

    respuesta = client.post(
        f"/api/habitaciones/{habitacion_id}/imagenes",
        files={"archivo": ("foto.png", FIRMA_PNG, "image/png")},
        headers=recepcion_headers,
    )

    assert respuesta.status_code == 403


def test_borrar_principal_promueve_otra(
    client: TestClient,
    admin_headers: dict[str, str],
    media_dir,
) -> None:
    habitacion_id = _crear_habitacion(client, admin_headers, 906)
    primera = _subir_imagen(client, admin_headers, habitacion_id, "a.png")
    segunda = _subir_imagen(client, admin_headers, habitacion_id, "b.png")

    assert primera["esPrincipal"] is True
    assert segunda["esPrincipal"] is False

    eliminada = client.delete(
        f"/api/habitaciones/{habitacion_id}/imagenes/{primera['id']}",
        headers=admin_headers,
    )
    assert eliminada.status_code == 204

    detalle = client.get(
        f"/api/habitaciones/{habitacion_id}", headers=admin_headers
    ).json()
    assert detalle["imagenPrincipalUrl"] == segunda["url"]
    assert [imagen["id"] for imagen in detalle["imagenes"]] == [segunda["id"]]
    assert detalle["imagenes"][0]["esPrincipal"] is True


def test_listar_incluye_imagen_principal_url(
    client: TestClient,
    admin_headers: dict[str, str],
    media_dir,
) -> None:
    habitacion_id = _crear_habitacion(client, admin_headers, 907)
    _subir_imagen(client, admin_headers, habitacion_id, "foto.png")

    listado = client.get("/api/habitaciones", headers=admin_headers)

    assert listado.status_code == 200
    item = listado.json()[0]
    assert item["imagenPrincipalUrl"].startswith("/media/")
    assert item["imagenes"][0]["esPrincipal"] is True
    assert item["imagenes"][0]["url"].startswith("/media/")


def test_marcar_imagen_principal(
    client: TestClient,
    admin_headers: dict[str, str],
    media_dir,
) -> None:
    habitacion_id = _crear_habitacion(client, admin_headers, 908)
    primera = _subir_imagen(client, admin_headers, habitacion_id, "a.png")
    segunda = _subir_imagen(client, admin_headers, habitacion_id, "b.png")

    marcada = client.patch(
        f"/api/habitaciones/{habitacion_id}/imagenes/{segunda['id']}/principal",
        headers=admin_headers,
    )

    assert marcada.status_code == 200
    assert marcada.json()["esPrincipal"] is True

    detalle = client.get(
        f"/api/habitaciones/{habitacion_id}", headers=admin_headers
    ).json()
    assert detalle["imagenPrincipalUrl"] == segunda["url"]
    assert detalle["imagenes"][0]["id"] == primera["id"]
    assert detalle["imagenes"][0]["esPrincipal"] is False
    assert detalle["imagenes"][1]["id"] == segunda["id"]
    assert detalle["imagenes"][1]["esPrincipal"] is True


def test_maximo_imagenes_devuelve_409(
    client: TestClient,
    admin_headers: dict[str, str],
    media_dir,
) -> None:
    habitacion_id = _crear_habitacion(client, admin_headers, 909)
    for i in range(10):
        _subir_imagen(client, admin_headers, habitacion_id, f"foto_{i}.png")

    respuesta = client.post(
        f"/api/habitaciones/{habitacion_id}/imagenes",
        files={"archivo": ("foto_10.png", FIRMA_PNG, "image/png")},
        headers=admin_headers,
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["code"] == "MAXIMO_IMAGENES"
