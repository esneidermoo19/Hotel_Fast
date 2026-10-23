import re

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import app, documentacion_habilitada


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


def test_cors_permite_puertos_locales_en_desarrollo(
    client: TestClient,
) -> None:
    permitido = client.get(
        "/api/health",
        headers={"Origin": "http://localhost:54321"},
    )
    externo = client.get(
        "/api/health",
        headers={"Origin": "https://sitio-externo.example"},
    )

    assert permitido.headers["access-control-allow-origin"] == "http://localhost:54321"
    assert "access-control-allow-origin" not in externo.headers


def test_documentacion_solo_se_publica_con_docs_enabled_en_produccion() -> None:
    desarrollo = Settings(_env_file=None, environment="development")
    produccion = Settings(
        _env_file=None,
        environment="production",
        secret_key="clave-segura-de-pruebas-con-longitud-1234",
        database_url="postgresql+psycopg://u:p@h:5432/db",
    )
    produccion_con_docs = Settings(
        _env_file=None,
        environment="production",
        secret_key="clave-segura-de-pruebas-con-longitud-1234",
        database_url="postgresql+psycopg://u:p@h:5432/db",
        docs_enabled=True,
    )

    assert documentacion_habilitada(desarrollo) is True
    assert documentacion_habilitada(produccion) is False
    assert documentacion_habilitada(produccion_con_docs) is True


def test_raiz_responde_info_del_servicio(client: TestClient) -> None:
    respuesta = client.get("/")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "nombre": "Hotel Fast - API de gestion hotelera",
        "version": "1.0.0",
        "estado": "ok",
        "salud": "/api/health",
        "documentacion": "/docs",
    }


def test_documentacion_disponible_fuera_de_produccion(client: TestClient) -> None:
    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_parametro_solo_activos_usa_camel_case_en_openapi() -> None:
    parametros = app.openapi()["paths"]["/api/usuarios"]["get"]["parameters"]
    nombres = {parametro["name"] for parametro in parametros}

    assert "soloActivos" in nombres
    assert "solo_activos" not in nombres
