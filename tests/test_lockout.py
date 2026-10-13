import pytest
from fastapi.testclient import TestClient

from app.core import lockout
from app.core.config import settings
from app.models import Usuario


def test_bloqueo_tras_alcanzar_el_maximo_de_intentos() -> None:
    for _ in range(settings.login_max_attempts):
        lockout.registrar_intento_fallido("usuario@example.com")

    assert lockout.esta_bloqueado("usuario@example.com") is True
    assert lockout.esta_bloqueado("otro@example.com") is False


def test_limpiar_intentos_desbloquea() -> None:
    for _ in range(settings.login_max_attempts):
        lockout.registrar_intento_fallido("u")

    lockout.limpiar_intentos("u")

    assert lockout.esta_bloqueado("u") is False


def test_bloqueo_deshabilitado_no_cuenta(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "login_lockout_enabled", False)

    for _ in range(settings.login_max_attempts + 1):
        lockout.registrar_intento_fallido("u")

    assert lockout.esta_bloqueado("u") is False


def test_login_bloqueado_devuelve_429_con_retry_after(
    client: TestClient,
    admin_user: Usuario,
) -> None:
    for _ in range(settings.login_max_attempts):
        client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "incorrecta"},
        )

    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "test-password-123"},
    )

    assert response.status_code == 429
    assert response.json()["code"] == "CUENTA_BLOQUEADA"
    assert response.headers["retry-after"] == str(settings.login_lockout_minutes * 60)


def test_login_correcto_limpia_los_intentos(
    client: TestClient,
    admin_user: Usuario,
) -> None:
    client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "incorrecta"},
    )

    correcto = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "test-password-123"},
    )

    assert correcto.status_code == 200
    assert lockout.esta_bloqueado("admin") is False
