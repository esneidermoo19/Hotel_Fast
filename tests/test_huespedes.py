from datetime import date

import pytest
from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from app.services import huesped_service
from tests.factories import (
    crear_habitacion,
    crear_huesped,
    crear_reserva,
    crear_usuario,
)


def huesped_payload(numero: str, **cambios: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "tipoDocumento": "CC",
        "numeroDocumento": numero,
        "nombres": "Juan",
        "apellidos": "Perez",
        "email": "juan.perez@example.com",
        "telefono": "+573001234567",
        "nacionalidad": "Colombiana",
        "fechaNacimiento": "1990-01-15",
        "direccion": "Calle 123",
        "observaciones": "Huesped de prueba",
    }
    payload.update(cambios)
    return payload


def test_crud_completo_huespedes(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    creado = client.post(
        "/api/huespedes",
        json=huesped_payload("1111111111"),
        headers=admin_headers,
    )
    assert creado.status_code == 201
    huesped = creado.json()
    assert huesped["numeroDocumento"] == "1111111111"
    assert huesped["tipoDocumento"] == "CC"
    huesped_id = huesped["id"]

    listado = client.get("/api/huespedes", headers=admin_headers)
    assert listado.status_code == 200
    pagina = listado.json()
    assert pagina["total"] == 1
    assert pagina["pagina"] == 1
    assert [item["id"] for item in pagina["items"]] == [huesped_id]

    detalle = client.get(
        f"/api/huespedes/{huesped_id}", headers=admin_headers
    )
    assert detalle.status_code == 200
    assert detalle.json()["nombres"] == "Juan"

    actualizado = client.put(
        f"/api/huespedes/{huesped_id}",
        json=huesped_payload("1111111111", nombres="Juan Carlos"),
        headers=admin_headers,
    )
    assert actualizado.status_code == 200
    assert actualizado.json()["nombres"] == "Juan Carlos"

    eliminado = client.delete(
        f"/api/huespedes/{huesped_id}", headers=admin_headers
    )
    assert eliminado.status_code == 204
    assert (
        client.get(
            f"/api/huespedes/{huesped_id}", headers=admin_headers
        ).status_code
        == 404
    )


def test_busqueda_q_sin_distinguir_mayusculas(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    client.post(
        "/api/huespedes",
        json=huesped_payload("2222222222", nombres="Juan", apellidos="Perez"),
        headers=admin_headers,
    )
    client.post(
        "/api/huespedes",
        json=huesped_payload("3333333333", nombres="Maria", apellidos="Gomez"),
        headers=admin_headers,
    )

    por_nombre = client.get(
        "/api/huespedes", params={"q": "juan"}, headers=admin_headers
    )
    assert por_nombre.status_code == 200
    assert por_nombre.json()["total"] == 1
    assert por_nombre.json()["items"][0]["apellidos"] == "Perez"

    por_apellido = client.get(
        "/api/huespedes", params={"q": "GOMEZ"}, headers=admin_headers
    )
    assert por_apellido.json()["total"] == 1

    por_documento = client.get(
        "/api/huespedes", params={"q": "333333"}, headers=admin_headers
    )
    assert por_documento.json()["total"] == 1


def test_filtros_tipo_y_numero_documento(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    client.post(
        "/api/huespedes",
        json=huesped_payload("4444444444", tipoDocumento="CC"),
        headers=admin_headers,
    )
    client.post(
        "/api/huespedes",
        json=huesped_payload("4444444444", tipoDocumento="CE"),
        headers=admin_headers,
    )

    por_tipo = client.get(
        "/api/huespedes",
        params={"tipoDocumento": "CE"},
        headers=admin_headers,
    )
    assert por_tipo.json()["total"] == 1
    assert por_tipo.json()["items"][0]["tipoDocumento"] == "CE"

    por_numero = client.get(
        "/api/huespedes",
        params={"numeroDocumento": "4444444444"},
        headers=admin_headers,
    )
    assert por_numero.json()["total"] == 2


def test_paginacion(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    for numero in ("5000000001", "5000000002", "5000000003"):
        client.post(
            "/api/huespedes",
            json=huesped_payload(numero),
            headers=admin_headers,
        )

    primera = client.get(
        "/api/huespedes",
        params={"pagina": 1, "tamano": 2},
        headers=admin_headers,
    )
    segunda = client.get(
        "/api/huespedes",
        params={"pagina": 2, "tamano": 2},
        headers=admin_headers,
    )
    assert primera.json()["total"] == 3
    assert primera.json()["pagina"] == 1
    assert primera.json()["tamano"] == 2
    assert len(primera.json()["items"]) == 2
    assert segunda.json()["pagina"] == 2
    assert segunda.json()["tamano"] == 2
    assert segunda.json()["total"] == 3
    assert len(segunda.json()["items"]) == 1
    ids_primera = [item["id"] for item in primera.json()["items"]]
    ids_segunda = [item["id"] for item in segunda.json()["items"]]
    assert not set(ids_primera) & set(ids_segunda)
    assert len(set(ids_primera + ids_segunda)) == 3


@pytest.mark.parametrize("tamano", [0, 101])
def test_listar_huespedes_rechaza_tamano_fuera_de_rango(
    client: TestClient,
    admin_headers: dict[str, str],
    tamano: int,
) -> None:
    response = client.get(
        "/api/huespedes",
        params={"pagina": 1, "tamano": tamano},
        headers=admin_headers,
    )

    assert response.status_code == 422
    assert set(response.json()) == {"detail", "code", "errors"}
    assert response.json()["code"] == "VALIDACION"
    assert response.json()["errors"]


def test_documento_duplicado_devuelve_409(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    payload = huesped_payload("6666666666")
    primera = client.post(
        "/api/huespedes", json=payload, headers=admin_headers
    )
    segunda = client.post(
        "/api/huespedes", json=payload, headers=admin_headers
    )
    assert primera.status_code == 201
    assert segunda.status_code == 409
    assert segunda.json()["detail"] == (
        "HUESPED_DUPLICADO: ya existe un huesped con CC 6666666666"
    )
    assert segunda.json()["code"] == "CONFLICTO"


def test_integrity_error_por_documento_duplicado_devuelve_409(
    client: TestClient,
    admin_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = huesped_payload("6767676767")
    primero = client.post(
        "/api/huespedes", json=payload, headers=admin_headers
    )
    assert primero.status_code == 201

    monkeypatch.setattr(
        huesped_service, "_existe_documento", lambda *args, **kwargs: False
    )
    segundo = client.post(
        "/api/huespedes", json=payload, headers=admin_headers
    )

    assert segundo.status_code == 409
    assert segundo.json()["detail"] == (
        "HUESPED_DUPLICADO: ya existe un huesped con CC 6767676767"
    )
    assert segundo.json()["code"] == "CONFLICTO"


def test_mismo_numero_distinto_tipo_esta_permitido(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    primera = client.post(
        "/api/huespedes",
        json=huesped_payload("7777777777", tipoDocumento="CC"),
        headers=admin_headers,
    )
    segunda = client.post(
        "/api/huespedes",
        json=huesped_payload("7777777777", tipoDocumento="TI"),
        headers=admin_headers,
    )
    assert primera.status_code == 201
    assert segunda.status_code == 201


def test_actualizar_a_documento_existente_devuelve_409(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    client.post(
        "/api/huespedes",
        json=huesped_payload("8888888881"),
        headers=admin_headers,
    )
    otro = client.post(
        "/api/huespedes",
        json=huesped_payload("8888888882"),
        headers=admin_headers,
    )
    otro_id = otro.json()["id"]

    respuesta = client.put(
        f"/api/huespedes/{otro_id}",
        json=huesped_payload("8888888881"),
        headers=admin_headers,
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == (
        "HUESPED_DUPLICADO: ya existe un huesped con CC 8888888881"
    )


def test_eliminar_con_reservas_devuelve_409(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    db = TestingSessionLocal()
    try:
        usuario = crear_usuario(
            db, username="resuser", email="resuser@example.com"
        )
        habitacion = crear_habitacion(db, numero=701)
        huesped = crear_huesped(db, numero_documento="9999999999")
        crear_reserva(
            db,
            huesped=huesped,
            habitacion=habitacion,
            usuario=usuario,
        )
        huesped_id = huesped.id
    finally:
        db.close()

    respuesta = client.delete(
        f"/api/huespedes/{huesped_id}", headers=admin_headers
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == (
        "HUESPED_CON_RESERVAS: no se puede eliminar un huesped con reservas"
    )


def test_huesped_inexistente_devuelve_404(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    lectura = client.get("/api/huespedes/9999", headers=admin_headers)
    eliminacion = client.delete("/api/huespedes/9999", headers=admin_headers)
    assert lectura.status_code == eliminacion.status_code == 404
    assert lectura.json()["detail"] == "No se encontro el huesped"
    assert eliminacion.json()["detail"] == "No se encontro el huesped"


def test_recepcion_puede_consultar_crear_y_actualizar(
    client: TestClient,
    admin_headers: dict[str, str],
    recepcion_headers: dict[str, str],
) -> None:
    creado = client.post(
        "/api/huespedes",
        json=huesped_payload("1212121212"),
        headers=recepcion_headers,
    )
    assert creado.status_code == 201
    huesped_id = creado.json()["id"]

    assert (
        client.get("/api/huespedes", headers=recepcion_headers).status_code
        == 200
    )
    actualizado = client.put(
        f"/api/huespedes/{huesped_id}",
        json=huesped_payload("1212121212", nombres="Pedro"),
        headers=recepcion_headers,
    )
    assert actualizado.status_code == 200
    assert actualizado.json()["nombres"] == "Pedro"


def test_eliminar_requiere_admin(
    client: TestClient,
    admin_headers: dict[str, str],
    recepcion_headers: dict[str, str],
) -> None:
    creado = client.post(
        "/api/huespedes",
        json=huesped_payload("1313131313"),
        headers=admin_headers,
    )
    huesped_id = creado.json()["id"]

    respuesta = client.delete(
        f"/api/huespedes/{huesped_id}", headers=recepcion_headers
    )
    assert respuesta.status_code == 403


def test_nombres_se_guardan_sin_espacios_sobrantes(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    creado = client.post(
        "/api/huespedes",
        json=huesped_payload(
            "1414141414",
            nombres="  Juan   Carlos  ",
            apellidos="  Perez   Gomez ",
        ),
        headers=admin_headers,
    )
    assert creado.status_code == 201
    assert creado.json()["nombres"] == "Juan Carlos"
    assert creado.json()["apellidos"] == "Perez Gomez"


def test_reservas_de_huesped_ordenadas_por_entrada_desc(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    db = TestingSessionLocal()
    try:
        usuario = crear_usuario(
            db, username="resuser2", email="resuser2@example.com"
        )
        habitacion = crear_habitacion(db, numero=702)
        huesped = crear_huesped(db, numero_documento="1515151515")
        crear_reserva(
            db,
            huesped=huesped,
            habitacion=habitacion,
            usuario=usuario,
            codigo="RES-2026-000011",
            fecha_entrada=date(2026, 10, 15),
            fecha_salida=date(2026, 10, 18),
        )
        crear_reserva(
            db,
            huesped=huesped,
            habitacion=habitacion,
            usuario=usuario,
            codigo="RES-2026-000012",
            fecha_entrada=date(2026, 11, 1),
            fecha_salida=date(2026, 11, 3),
        )
        crear_reserva(
            db,
            huesped=huesped,
            habitacion=habitacion,
            usuario=usuario,
            codigo="RES-2026-000013",
            fecha_entrada=date(2026, 11, 1),
            fecha_salida=date(2026, 11, 4),
        )
        huesped_id = huesped.id
    finally:
        db.close()

    respuesta = client.get(
        f"/api/huespedes/{huesped_id}/reservas",
        params={"pagina": 1, "tamano": 2},
        headers=admin_headers,
    )
    assert respuesta.status_code == 200
    pagina = respuesta.json()
    assert pagina["total"] == 3
    assert pagina["pagina"] == 1
    assert pagina["tamano"] == 2
    assert [item["codigo"] for item in pagina["items"]] == [
        "RES-2026-000013",
        "RES-2026-000012",
    ]
    pagina_dos = client.get(
        f"/api/huespedes/{huesped_id}/reservas",
        params={"pagina": 2, "tamano": 2},
        headers=admin_headers,
    )
    assert pagina_dos.status_code == 200
    assert pagina_dos.json()["pagina"] == 2
    assert pagina_dos.json()["tamano"] == 2
    assert pagina_dos.json()["total"] == 3
    todos_los_ids = [item["id"] for item in pagina["items"] + pagina_dos.json()["items"]]
    assert len(todos_los_ids) == 3
    assert len(set(todos_los_ids)) == 3
    assert pagina_dos.json()["items"][0]["codigo"] == "RES-2026-000011"

    inexistente = client.get(
        "/api/huespedes/9999/reservas", headers=admin_headers
    )
    assert inexistente.status_code == 404


@pytest.mark.parametrize("tamano", [0, 101])
def test_listar_reservas_huesped_rechaza_tamano_fuera_de_rango(
    client: TestClient,
    admin_headers: dict[str, str],
    tamano: int,
) -> None:
    response = client.get(
        "/api/huespedes/1/reservas",
        params={"pagina": 1, "tamano": tamano},
        headers=admin_headers,
    )

    assert response.status_code == 422
    assert set(response.json()) == {"detail", "code", "errors"}
    assert response.json()["code"] == "VALIDACION"
    assert response.json()["errors"]


@pytest.mark.parametrize(
    "cambios",
    [
        {"numeroDocumento": "ABC"},
        {"numeroDocumento": "A" * 21},
        {"numeroDocumento": "AB-12"},
        {"email": "no-es-email"},
        {"telefono": "123"},
        {"telefono": "abc1234567"},
        {"fechaNacimiento": "2999-01-01"},
        {"nombres": "   "},
    ],
)
def test_validacion_de_huesped_devuelve_422(
    client: TestClient,
    admin_headers: dict[str, str],
    cambios: dict[str, object],
) -> None:
    respuesta = client.post(
        "/api/huespedes",
        json=huesped_payload("1616161616", **cambios),
        headers=admin_headers,
    )
    assert respuesta.status_code == 422


def test_rutas_requieren_token(client: TestClient) -> None:
    respuesta = client.get("/api/huespedes")
    assert respuesta.status_code == 401
    assert respuesta.headers["www-authenticate"] == "Bearer"
