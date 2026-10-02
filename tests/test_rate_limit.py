import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.limiter import limiter

INTENTOS = 6


@pytest.fixture
def limiter_activo() -> None:
    limiter.enabled = True
    yield
    limiter.enabled = False


def test_login_se_bloquea_tras_superar_el_limite(
    client: TestClient,
    admin_user,
    limiter_activo: None,
) -> None:
    codigos = [
        client.post(
            "/api/auth/login",
            json={
                "username": "admin",
                "email": "admin@example.com",
                "password": "incorrecta",
            },
        ).status_code
        for _ in range(INTENTOS)
    ]

    assert 429 in codigos
    assert codigos[0] == 401


def test_429_usa_el_sobre_de_error_con_codigo(
    client: TestClient,
    admin_user,
    limiter_activo: None,
) -> None:
    respuesta_bloqueo = None
    for _ in range(INTENTOS):
        respuesta_bloqueo = client.post(
            "/api/auth/login",
            json={
                "username": "admin",
                "email": "admin@example.com",
                "password": "incorrecta",
            },
        )
        if respuesta_bloqueo.status_code == 429:
            break

    cuerpo = respuesta_bloqueo.json()
    assert respuesta_bloqueo.status_code == 429
    assert cuerpo["code"] == "DEMASIADAS_SOLICITUDES"
    assert respuesta_bloqueo.headers["retry-after"] == "60"


def test_refresh_tambien_es_limitado(
    client: TestClient,
    admin_user,
    limiter_activo: None,
) -> None:
    codigos = [
        client.post(
            "/api/auth/refresh",
            json={"refreshToken": f"token-{indice}"},
        ).status_code
        for indice in range(INTENTOS)
    ]

    assert 429 in codigos


def test_limite_configurado_por_defecto() -> None:
    assert settings.login_rate_limit == "5/minute"
