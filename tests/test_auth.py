import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.models import Usuario
from app.routers.auth import router
from app.services import auth_service


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
    assert response.json() == {
        "detail": "Credenciales incorrectas",
        "code": "NO_AUTORIZADO",
    }
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
    cuerpo = response.json()
    assert cuerpo["id"] == admin_user.id
    assert cuerpo["username"] == "admin"
    assert cuerpo["email"] == "admin@example.com"
    assert cuerpo["nombre"] == "Administrador"
    assert cuerpo["role"] == "ADMIN"
    assert cuerpo["activo"] is True


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


def test_logout_requiere_refresh_token_y_devuelve_204(
    client: TestClient,
    admin_user: Usuario,
) -> None:
    response = client.post(
        "/api/auth/logout",
        json={"refreshToken": "token-cualquiera"},
    )

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


@pytest.mark.parametrize(
    ("campo", "identificador"),
    [("username", "ADMIN"), ("email", "ADMIN@EXAMPLE.COM")],
)
def test_login_acepta_username_o_email(
    client: TestClient,
    admin_user: Usuario,
    campo: str,
    identificador: str,
) -> None:
    response = client.post(
        "/api/auth/login",
        json={campo: identificador, "password": "test-password-123"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == admin_user.id


def test_login_rechaza_identificador_ausente(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/auth/login",
        json={"password": "test-password-123"},
    )

    assert response.status_code == 422


def test_login_usuario_inexistente_verifica_hash_falso(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    hashes_verificados: list[str] = []

    def verificar(password: str, password_hash: str) -> bool:
        hashes_verificados.append(password_hash)
        return False

    monkeypatch.setattr(auth_service, "verify_password", verificar)
    response = client.post(
        "/api/auth/login",
        json={"username": "no-existe", "password": "cualquier-clave"},
    )

    assert response.status_code == 401
    assert hashes_verificados == [auth_service._HASH_FALSO]


@pytest.mark.parametrize(
    "authorization",
    [None, "Bearer token-invalido"],
)
def test_me_siempre_responde_401_bearer_sin_token_valido(
    client: TestClient,
    authorization: str | None,
) -> None:
    headers = {"Authorization": authorization} if authorization else {}
    response = client.get("/api/auth/me", headers=headers)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json()["code"] == "TOKEN_INVALIDO"
    assert response.json()["errors"] == []
