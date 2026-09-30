import jwt
import pytest
from fastapi.testclient import TestClient

from app.controllers.auth import router
from app.core.config import settings
from app.models import Usuario


def test_auth_router_prefix() -> None:
    assert router.prefix == "/api/auth"


def test_login_correcto_ignora_campos_extra(
    client: TestClient,
    admin_user: Usuario,
) -> None:
    response = client.post(
        "/api/auth/login",
        json={
            "username": "ADMIN@EXAMPLE.COM",
            "email": "ADMIN@EXAMPLE.COM",
            "password": "test-password-123",
            "campoExtra": "ignorado",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["tokenType"] == "bearer"
    assert body["id"] == admin_user.id
    assert body["username"] == "admin"
    assert body["email"] == "admin@example.com"
    assert body["nombre"] == "Administrador"
    assert body["role"] == "ADMIN"
    assert "token" in body


def test_login_incorrecto_devuelve_401_y_bearer(
    client: TestClient,
    admin_user: Usuario,
) -> None:
    response = client.post(
        "/api/auth/login",
        json={
            "username": "admin",
            "email": "admin",
            "password": "incorrecta",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Credenciales incorrectas"}
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize("authorization", [None, "Bearer token-invalido"])
def test_me_rechaza_token_ausente_o_invalido(
    client: TestClient,
    authorization: str | None,
) -> None:
    headers = {"Authorization": authorization} if authorization else {}
    response = client.get("/api/auth/me", headers=headers)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_devuelve_usuario_del_token(
    client: TestClient,
    admin_user: Usuario,
    admin_headers: dict[str, str],
) -> None:
    response = client.get("/api/auth/me", headers=admin_headers)

    assert response.status_code == 200
    assert response.json() == {
        "id": admin_user.id,
        "username": "admin",
        "email": "admin@example.com",
        "nombre": "Administrador",
        "role": "ADMIN",
    }


def test_login_token_contiene_sub_role_y_exp(
    client: TestClient,
    admin_user: Usuario,
) -> None:
    response = client.post(
        "/api/auth/login",
        json={
            "username": "admin",
            "email": "admin",
            "password": "test-password-123",
        },
    )
    payload = jwt.decode(
        response.json()["token"],
        settings.secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    assert payload["sub"] == str(admin_user.id)
    assert payload["role"] == "ADMIN"
    assert "exp" in payload


def test_logout_requiere_token_y_devuelve_204(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.post("/api/auth/logout", headers=admin_headers)

    assert response.status_code == 204
    assert response.content == b""


def test_login_busca_por_username_case_insensitive(
    client: TestClient,
    admin_user: Usuario,
) -> None:
    response = client.post(
        "/api/auth/login",
        json={
            "username": "ADMIN",
            "email": "ADMIN",
            "password": "test-password-123",
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == admin_user.id
