import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import RefreshTokenInvalidoError
from app.core.security import hash_refresh_token
from app.models import RefreshToken, Usuario
from app.services import refresh_token_service

CREDENCIALES = {
    "username": "admin",
    "email": "admin@example.com",
    "password": "test-password-123",
}


def _login(client: TestClient) -> dict[str, object]:
    response = client.post("/api/auth/login", json=CREDENCIALES)
    assert response.status_code == 200
    return response.json()


def test_login_devuelve_access_y_refresh_token(
    client: TestClient,
    admin_user: Usuario,
) -> None:
    cuerpo = _login(client)

    assert cuerpo["tokenType"] == "bearer"
    assert cuerpo["refreshToken"]
    assert cuerpo["expiresIn"] == settings.access_token_expire_minutes * 60
    assert cuerpo["role"] == "ADMIN"


def test_refresh_token_se_guarda_solo_hasheado(
    client: TestClient,
    db_session: Session,
    admin_user: Usuario,
) -> None:
    cuerpo = _login(client)
    refresh_token = str(cuerpo["refreshToken"])

    registros = db_session.scalars(select(RefreshToken)).all()

    assert len(registros) == 1
    assert registros[0].token_hash == hash_refresh_token(refresh_token)
    assert refresh_token not in registros[0].token_hash


def test_refresh_rota_el_token_y_devuelve_nuevo_access(
    client: TestClient,
    admin_user: Usuario,
) -> None:
    login = _login(client)

    response = client.post(
        "/api/auth/refresh",
        json={"refreshToken": login["refreshToken"]},
    )

    assert response.status_code == 200
    cuerpo = response.json()
    assert cuerpo["refreshToken"] != login["refreshToken"]
    assert cuerpo["tokenType"] == "bearer"
    payload = jwt.decode(
        cuerpo["token"],
        settings.secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    assert payload["sub"] == str(admin_user.id)
    assert payload["role"] == "ADMIN"


def test_access_token_nuevo_sirve_para_llamar_la_api(
    client: TestClient,
    admin_user: Usuario,
) -> None:
    login = _login(client)
    rotado = client.post(
        "/api/auth/refresh",
        json={"refreshToken": login["refreshToken"]},
    ).json()

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {rotado['token']}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == admin_user.id


def test_reuso_del_refresh_token_revoca_la_familia(
    client: TestClient,
    db_session: Session,
    admin_user: Usuario,
) -> None:
    login = _login(client)
    primero = client.post(
        "/api/auth/refresh",
        json={"refreshToken": login["refreshToken"]},
    ).json()

    # Reutilizar el token ya rotado se trata como robo de credenciales.
    reuse = client.post(
        "/api/auth/refresh",
        json={"refreshToken": login["refreshToken"]},
    )
    assert reuse.status_code == 401
    assert reuse.json()["code"] == "REFRESH_TOKEN_INVALIDO"

    # ... y mata tambien el token emitido en la rotacion valida.
    segundo = client.post(
        "/api/auth/refresh",
        json={"refreshToken": primero["refreshToken"]},
    )
    assert segundo.status_code == 401

    vivos = db_session.scalars(
        select(RefreshToken).where(RefreshToken.revocado_en.is_(None))
    ).all()
    assert vivos == []


def test_refresh_token_inexistente_devuelve_401(
    client: TestClient,
    admin_user: Usuario,
) -> None:
    response = client.post(
        "/api/auth/refresh",
        json={"refreshToken": "token-que-nunca-se-emitio"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Refresh token invalido",
        "code": "REFRESH_TOKEN_INVALIDO",
    }
    assert response.headers["www-authenticate"] == "Bearer"


def test_refresh_token_vencido_devuelve_401(
    client: TestClient,
    db_session: Session,
    admin_user: Usuario,
) -> None:
    cuerpo = _login(client)
    registro = db_session.scalar(select(RefreshToken))
    registro.expira_en = registro.expira_en.replace(year=2000)
    db_session.commit()

    response = client.post(
        "/api/auth/refresh",
        json={"refreshToken": cuerpo["refreshToken"]},
    )

    assert response.status_code == 401
    assert "expirado" in response.json()["detail"]


def test_logout_revoca_el_refresh_token(
    client: TestClient,
    admin_user: Usuario,
) -> None:
    login = _login(client)

    logout = client.post(
        "/api/auth/logout",
        json={"refreshToken": login["refreshToken"]},
    )
    assert logout.status_code == 204
    assert logout.content == b""

    refresh = client.post(
        "/api/auth/refresh",
        json={"refreshToken": login["refreshToken"]},
    )
    assert refresh.status_code == 401


def test_logout_es_idempotente(client: TestClient, admin_user: Usuario) -> None:
    login = _login(client)

    for _ in range(2):
        response = client.post(
            "/api/auth/logout",
            json={"refreshToken": login["refreshToken"]},
        )
        assert response.status_code == 204


def test_rotar_sin_commit_previo_persiste(
    client: TestClient,
    db_session: Session,
    admin_user: Usuario,
) -> None:
    cuerpo = _login(client)
    usuario, nuevo = refresh_token_service.rotar_refresh_token(
        db_session,
        str(cuerpo["refreshToken"]),
    )

    assert usuario.id == admin_user.id
    assert nuevo != cuerpo["refreshToken"]
    assert db_session.scalar(
        select(RefreshToken).where(RefreshToken.revocado_en.is_(None))
    ).token_hash == hash_refresh_token(nuevo)


def test_rotar_token_ajeno_devuelve_error_de_dominio(
    db_session: Session,
    admin_user: Usuario,
) -> None:
    with pytest.raises(RefreshTokenInvalidoError):
        refresh_token_service.rotar_refresh_token(db_session, "inexistente")


def test_revocar_todos_del_usuario_cierra_todas_las_sesiones(
    client: TestClient,
    db_session: Session,
    admin_user: Usuario,
) -> None:
    login = _login(client)
    rotado = client.post(
        "/api/auth/refresh",
        json={"refreshToken": login["refreshToken"]},
    ).json()

    refresh_token_service.revocar_todos_del_usuario(db_session, admin_user.id)

    for token in (login["refreshToken"], rotado["refreshToken"]):
        response = client.post("/api/auth/refresh", json={"refreshToken": token})
        assert response.status_code == 401


def test_limpiar_vencidos_borra_historico(
    client: TestClient,
    db_session: Session,
    admin_user: Usuario,
) -> None:
    _login(client)
    registro = db_session.scalar(select(RefreshToken))
    registro.expira_en = registro.expira_en.replace(year=2000)
    db_session.commit()

    assert refresh_token_service.limpiar_vencidos(db_session) == 1
    assert db_session.scalars(select(RefreshToken)).all() == []


def test_refresh_requiere_cuerpo_con_refresh_token(client: TestClient) -> None:
    response = client.post("/api/auth/refresh", json={})

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDACION"
    assert response.json()["errors"][0]["campo"] == "refreshToken"
