from fastapi.testclient import TestClient

from app.core.errors import (
    ConflictoError,
    NoAutorizadoError,
    ProhibidoError,
    TokenInvalidoError,
)


def test_sobre_de_error_incluye_detail_y_code(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.get("/api/habitaciones/9999", headers=admin_headers)

    assert response.status_code == 404
    cuerpo = response.json()
    assert cuerpo["code"] == "NO_ENCONTRADO"
    assert cuerpo["detail"]
    assert "errors" not in cuerpo


def test_token_invalido_usa_codigo_español(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/habitaciones",
        headers={"Authorization": "Bearer no-es-un-jwt"},
    )

    assert response.status_code == 401
    assert response.json()["code"] == "TOKEN_INVALIDO"
    assert response.headers["www-authenticate"] == "Bearer"


def test_sin_permisos_usa_codigo_sin_permisos(
    client: TestClient,
    recepcion_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/habitaciones",
        json={
            "numero": 601,
            "tipo": "SIMPLE",
            "capacidad": 1,
            "precioPorNoche": 80,
        },
        headers=recepcion_headers,
    )

    assert response.status_code == 403
    assert response.json()["code"] == "SIN_PERMISOS"


def test_validacion_422_lista_campos_en_camel_case(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/habitaciones",
        json={
            "numero": 0,
            "tipo": "SIMPLE",
            "capacidad": 0,
            "precioPorNoche": 0,
        },
        headers=admin_headers,
    )

    assert response.status_code == 422
    cuerpo = response.json()
    assert cuerpo["code"] == "VALIDACION"
    campos = {detalle["campo"] for detalle in cuerpo["errors"]}
    assert campos == {"numero", "capacidad", "precioPorNoche"}
    assert all(detalle["mensaje"] for detalle in cuerpo["errors"])


def test_validacion_422_en_body_ignora_prefijo_body(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/habitaciones",
        json={
            "numero": 10,
            "tipo": "TIPO_INEXISTENTE",
            "capacidad": 1,
            "precioPorNoche": 10,
        },
        headers=admin_headers,
    )

    assert response.status_code == 422
    assert cuerpo_campo(response) == "tipo"


def cuerpo_campo(response) -> str:  # type: ignore[no-untyped-def]
    return response.json()["errors"][0]["campo"]


def test_conflicto_usa_codigo_conflicto(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    payload = {
        "numero": 777,
        "tipo": "DOBLE",
        "capacidad": 2,
        "precioPorNoche": 100,
    }
    client.post("/api/habitaciones", json=payload, headers=admin_headers)
    response = client.post("/api/habitaciones", json=payload, headers=admin_headers)

    assert response.status_code == 409
    assert response.json()["code"] == "CONFLICTO"


def test_todo_error_de_app_lleva_www_authenticate() -> None:
    assert NoAutorizadoError().headers == {"WWW-Authenticate": "Bearer"}
    assert TokenInvalidoError().headers == {"WWW-Authenticate": "Bearer"}
    assert ProhibidoError().status_code == 403
    assert ConflictoError().status_code == 409
