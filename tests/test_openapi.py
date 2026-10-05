import re

import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_operaciones_openapi_tienen_summary_tags_y_operation_id_unicos() -> None:
    especificacion = app.openapi()
    assert especificacion["info"]["version"] == "1.0.0"
    assert especificacion["info"]["title"] == "Hotel Fast - API de gestion hotelera"
    assert all(tag.get("description") for tag in especificacion["tags"])
    assert app.swagger_ui_parameters["persistAuthorization"] is True
    operation_ids: list[str] = []

    for ruta, metodos in especificacion["paths"].items():
        for metodo, operacion in metodos.items():
            if metodo not in {"get", "post", "put", "patch", "delete"}:
                continue
            assert operacion.get("summary"), f"{metodo.upper()} {ruta} sin summary"
            assert operacion.get("tags"), f"{metodo.upper()} {ruta} sin tags"
            assert operacion.get("operationId"), (
                f"{metodo.upper()} {ruta} sin operationId"
            )
            assert re.fullmatch(r"[a-z][A-Za-z0-9]*", operacion["operationId"])
            assert operacion.get("responses")
            assert all(
                respuesta.get("description")
                and respuesta["description"] != "Validation Error"
                for respuesta in operacion["responses"].values()
            ), f"{metodo.upper()} {ruta} tiene respuestas sin descripcion en espanol"
            operation_ids.append(operacion["operationId"])

    assert len(operation_ids) == len(set(operation_ids))


def test_operaciones_protegidas_rechazan_solicitudes_sin_token(
    client: TestClient,
) -> None:
    especificacion = app.openapi()
    operaciones_protegidas = [
        (metodo, ruta)
        for ruta, metodos in especificacion["paths"].items()
        for metodo, operacion in metodos.items()
        if metodo in {"get", "post", "put", "patch", "delete"}
        and operacion.get("security")
    ]

    assert operaciones_protegidas
    for metodo, ruta in operaciones_protegidas:
        ruta_con_parametros = re.sub(r"\{[^/]+\}", "1", ruta)
        respuesta = client.request(metodo.upper(), ruta_con_parametros)

        assert respuesta.status_code == 401, f"{metodo.upper()} {ruta}"
        assert respuesta.headers["www-authenticate"] == "Bearer"
        assert respuesta.json()["code"] == "TOKEN_INVALIDO"
        assert respuesta.json()["errors"] == []


@pytest.mark.parametrize("authorization", ["Bearer token-invalido", "Basic abc"])
def test_token_ausente_malformado_o_invalido_usa_reto_bearer(
    client: TestClient,
    authorization: str,
) -> None:
    respuesta = client.get(
        "/api/auth/me",
        headers={"Authorization": authorization},
    )

    assert respuesta.status_code == 401
    assert respuesta.headers["www-authenticate"] == "Bearer"
    assert respuesta.json() == {
        "detail": "Token de acceso invalido",
        "code": "TOKEN_INVALIDO",
        "errors": [],
    }
