import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Auditoria, RefreshToken, Usuario
from app.schemas.usuario import UsuarioCrear


def payload_usuario(**cambios: object) -> dict[str, object]:
    datos: dict[str, object] = {
        "username": "nuevo",
        "email": "nuevo@example.com",
        "nombre": "Nuevo Usuario",
        "password": "clave-fuerte-1",
        "role": "RECEPCION",
    }
    datos.update(cambios)
    return datos


def test_crear_usuario_normaliza_y_devuelve_201(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/usuarios",
        json=payload_usuario(username="Recepcion.Nueva", email="Nueva@Example.com"),
        headers=admin_headers,
    )

    assert response.status_code == 201
    cuerpo = response.json()
    assert cuerpo["username"] == "recepcion.nueva"
    assert cuerpo["email"] == "nueva@example.com"
    assert cuerpo["activo"] is True
    assert "password" not in cuerpo
    assert "passwordHash" not in cuerpo


def test_listar_y_obtener_usuario(
    client: TestClient,
    admin_headers: dict[str, str],
    admin_user: Usuario,
) -> None:
    client.post(
        "/api/usuarios",
        json=payload_usuario(),
        headers=admin_headers,
    )

    listado = client.get("/api/usuarios", headers=admin_headers)
    detalle = client.get(f"/api/usuarios/{admin_user.id}", headers=admin_headers)

    assert listado.status_code == 200
    assert listado.json()["total"] == 2
    assert len(listado.json()["items"]) == 2
    assert detalle.status_code == 200
    assert detalle.json()["id"] == admin_user.id


def test_listar_usuarios_filtra_y_pagina(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    client.post("/api/usuarios", json=payload_usuario(), headers=admin_headers)
    inactivo = client.post(
        "/api/usuarios",
        json=payload_usuario(
            username="inactivo",
            email="inactivo@example.com",
            role="ADMIN",
        ),
        headers=admin_headers,
    )
    assert inactivo.status_code == 201
    desactivado = client.post(
        f"/api/usuarios/{inactivo.json()['id']}/desactivar",
        headers=admin_headers,
    )
    assert desactivado.status_code == 200

    respuesta = client.get(
        "/api/usuarios",
        params={
            "rol": "RECEPCION",
            "activo": "true",
            "q": "NUEVO",
            "pagina": 1,
            "tamano": 1,
        },
        headers=admin_headers,
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["total"] == 1
    assert respuesta.json()["pagina"] == 1
    assert respuesta.json()["tamano"] == 1
    assert [item["username"] for item in respuesta.json()["items"]] == ["nuevo"]


def test_listar_usuarios_pagina_sin_repetir_ni_perder_registros(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    for indice in range(3):
        response = client.post(
            "/api/usuarios",
            json=payload_usuario(
                username=f"pagina{indice}",
                email=f"pagina{indice}@example.com",
            ),
            headers=admin_headers,
        )
        assert response.status_code == 201

    primera = client.get(
        "/api/usuarios",
        params={"pagina": 1, "tamano": 2},
        headers=admin_headers,
    )
    segunda = client.get(
        "/api/usuarios",
        params={"pagina": 2, "tamano": 2},
        headers=admin_headers,
    )
    pagina_uno = primera.json()
    pagina_dos = segunda.json()

    assert primera.status_code == segunda.status_code == 200
    assert pagina_uno["total"] == pagina_dos["total"] == 4
    assert (pagina_uno["pagina"], pagina_uno["tamano"]) == (1, 2)
    assert (pagina_dos["pagina"], pagina_dos["tamano"]) == (2, 2)
    ids_primera = [item["id"] for item in pagina_uno["items"]]
    ids_segunda = [item["id"] for item in pagina_dos["items"]]
    ids_paginados = ids_primera + ids_segunda
    assert not set(ids_primera) & set(ids_segunda)
    assert ids_paginados == sorted(ids_paginados)
    assert len(set(ids_paginados)) == 4


@pytest.mark.parametrize("tamano", [0, 101])
def test_listar_usuarios_rechaza_tamano_fuera_de_rango(
    client: TestClient,
    admin_headers: dict[str, str],
    tamano: int,
) -> None:
    response = client.get(
        "/api/usuarios",
        params={"pagina": 1, "tamano": tamano},
        headers=admin_headers,
    )

    assert response.status_code == 422
    assert set(response.json()) == {"detail", "code", "errors"}
    assert response.json()["code"] == "VALIDACION"
    assert response.json()["errors"]


def test_username_duplicado_devuelve_409_sin_distinguir_mayusculas(
    client: TestClient,
    admin_headers: dict[str, str],
    admin_user: Usuario,
) -> None:
    response = client.post(
        "/api/usuarios",
        json=payload_usuario(username="ADMIN", email="otro@example.com"),
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert response.json()["code"] == "CONFLICTO"
    assert "username" in response.json()["detail"]


def test_email_duplicado_devuelve_409(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/usuarios",
        json=payload_usuario(email="ADMIN@EXAMPLE.COM"),
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert "email" in response.json()["detail"]


def test_password_debil_devuelve_422_con_detalle_por_campo(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/usuarios",
        json=payload_usuario(password="corta"),
        headers=admin_headers,
    )

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDACION"
    assert response.json()["errors"][0]["campo"] == "password"


def test_password_sin_numero_devuelve_422(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/usuarios",
        json=payload_usuario(password="sololetraslargas"),
        headers=admin_headers,
    )

    assert response.status_code == 422
    assert "numero" in response.json()["detail"]


def test_actualizar_usuario_cambia_campos(
    client: TestClient,
    admin_headers: dict[str, str],
    recepcion_user: Usuario,
) -> None:
    response = client.put(
        f"/api/usuarios/{recepcion_user.id}",
        json={"nombre": "Recepcion Actualizada", "role": "ADMIN"},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["nombre"] == "Recepcion Actualizada"
    assert response.json()["role"] == "ADMIN"


def test_actualizar_usuario_inexistente_devuelve_404(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.put(
        "/api/usuarios/9999",
        json={"nombre": "Nobody"},
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert response.json()["code"] == "NO_ENCONTRADO"


def test_desactivar_usuario_revoca_sus_sesiones(
    client: TestClient,
    admin_headers: dict[str, str],
    recepcion_user: Usuario,
) -> None:
    login = client.post(
        "/api/auth/login",
        json={
            "username": "recepcion",
            "email": "recepcion@example.com",
            "password": "test-password-123",
        },
    ).json()

    desactivado = client.post(
        f"/api/usuarios/{recepcion_user.id}/desactivar",
        headers=admin_headers,
    )

    assert desactivado.status_code == 200
    assert desactivado.json()["activo"] is False

    refresh = client.post(
        "/api/auth/refresh",
        json={"refreshToken": login["refreshToken"]},
    )
    assert refresh.status_code == 401


def test_usuario_desactivado_no_puede_iniciar_sesion(
    client: TestClient,
    admin_headers: dict[str, str],
    recepcion_user: Usuario,
) -> None:
    client.post(
        f"/api/usuarios/{recepcion_user.id}/desactivar",
        headers=admin_headers,
    )

    login = client.post(
        "/api/auth/login",
        json={
            "username": "recepcion",
            "email": "recepcion@example.com",
            "password": "test-password-123",
        },
    )

    assert login.status_code == 401


def test_access_token_de_usuario_desactivado_deja_de_servir(
    client: TestClient,
    admin_headers: dict[str, str],
    recepcion_headers: dict[str, str],
    recepcion_user: Usuario,
) -> None:
    assert client.get("/api/auth/me", headers=recepcion_headers).status_code == 200

    client.post(
        f"/api/usuarios/{recepcion_user.id}/desactivar",
        headers=admin_headers,
    )

    assert client.get("/api/auth/me", headers=recepcion_headers).status_code == 401


def test_reactivar_usuario_devuelve_activo(
    client: TestClient,
    admin_headers: dict[str, str],
    recepcion_user: Usuario,
) -> None:
    client.post(
        f"/api/usuarios/{recepcion_user.id}/desactivar",
        headers=admin_headers,
    )

    response = client.post(
        f"/api/usuarios/{recepcion_user.id}/reactivar",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["activo"] is True


def test_admin_no_puede_desactivarse_a_si_mismo(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    """Con otro administrador activo, el guard que queda es el de cuenta propia."""
    client.post(
        "/api/usuarios",
        json=payload_usuario(username="admin2", email="admin2@example.com", role="ADMIN"),
        headers=admin_headers,
    )

    mi_id = client.get("/api/auth/me", headers=admin_headers).json()["id"]
    response = client.post(
        f"/api/usuarios/{mi_id}/desactivar",
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert "tu propia cuenta" in response.json()["detail"]


def test_servicio_bloquea_desactivar_al_ultimo_admin(
    db_session: Session,
    admin_user: Usuario,
) -> None:
    """El guard de ultimo administrador tiene prioridad sobre el de cuenta
    propia: si solo queda un admin, ese es el motivo real que se informa."""
    from app.services import usuario_service

    with pytest.raises(usuario_service.UltimoAdministradorError):
        usuario_service.desactivar_usuario(
            db_session,
            admin_user.id,
            usuario_actual=admin_user,
        )


def test_no_se_puede_degradar_al_ultimo_admin(
    client: TestClient,
    admin_headers: dict[str, str],
    admin_user: Usuario,
) -> None:
    response = client.put(
        f"/api/usuarios/{admin_user.id}",
        json={"role": "RECEPCION"},
        headers=admin_headers,
    )

    assert response.status_code == 409


def test_se_puede_desactivar_un_admin_hayendo_otro_activo(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    segundo = client.post(
        "/api/usuarios",
        json=payload_usuario(username="admin2", email="admin2@example.com", role="ADMIN"),
        headers=admin_headers,
    ).json()

    desactivado = client.post(
        f"/api/usuarios/{segundo['id']}/desactivar",
        headers=admin_headers,
    )

    assert desactivado.status_code == 200
    assert desactivado.json()["activo"] is False


def test_eliminar_propio_usuario_devuelve_409(
    client: TestClient,
    admin_headers: dict[str, str],
    admin_user: Usuario,
) -> None:
    response = client.delete(f"/api/usuarios/{admin_user.id}", headers=admin_headers)

    assert response.status_code == 409


def test_recepcion_no_puede_gestionar_usuarios(
    client: TestClient,
    recepcion_headers: dict[str, str],
) -> None:
    assert client.get("/api/usuarios", headers=recepcion_headers).status_code == 403
    assert (
        client.post(
            "/api/usuarios",
            json=payload_usuario(),
            headers=recepcion_headers,
        ).status_code
        == 403
    )


def test_rutas_de_usuarios_requieren_token(client: TestClient) -> None:
    assert client.get("/api/usuarios").status_code == 401


def test_cambiar_password_actualiza_y_cierra_sesiones(
    client: TestClient,
    recepcion_user: Usuario,
    db_session: Session,
) -> None:
    login = client.post(
        "/api/auth/login",
        json={
            "username": "recepcion",
            "email": "recepcion@example.com",
            "password": "test-password-123",
        },
    ).json()

    response = client.post(
        "/api/auth/cambiar-password",
        json={
            "passwordActual": "test-password-123",
            "passwordNuevo": "nueva-clave-99",
        },
        headers={"Authorization": f"Bearer {login['token']}"},
    )

    assert response.status_code == 200
    assert "nueva-clave-99" not in response.text

    # La sesión actual queda revocada: hay que volver a entrar.
    assert (
        client.post(
            "/api/auth/refresh",
            json={"refreshToken": login["refreshToken"]},
        ).status_code
        == 401
    )
    assert db_session.scalar(
        select(RefreshToken).where(RefreshToken.revocado_en.is_(None))
    ) is None

    nuevo_login = client.post(
        "/api/auth/login",
        json={
            "username": "recepcion",
            "email": "recepcion@example.com",
            "password": "nueva-clave-99",
        },
    )
    assert nuevo_login.status_code == 200


def test_cambiar_password_con_actual_incorrecta_devuelve_409(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/auth/cambiar-password",
        json={
            "passwordActual": "no-es-la-clave",
            "passwordNuevo": "nueva-clave-99",
        },
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert response.json()["code"] == "CONFLICTO"


def test_cambiar_password_reutilizada_devuelve_422(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/auth/cambiar-password",
        json={
            "passwordActual": "test-password-123",
            "passwordNuevo": "test-password-123",
        },
        headers=admin_headers,
    )

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDACION"


def test_cambiar_password_requiere_token(client: TestClient) -> None:
    response = client.post(
        "/api/auth/cambiar-password",
        json={"passwordActual": "a", "passwordNuevo": "b"},
    )

    assert response.status_code == 401


def test_auditoria_registra_creacion_de_usuario(
    client: TestClient,
    db_session: Session,
    admin_user: Usuario,
    admin_headers: dict[str, str],
) -> None:
    creado = client.post(
        "/api/usuarios",
        json=payload_usuario(),
        headers=admin_headers,
    ).json()

    registros = db_session.scalars(
        select(Auditoria).where(Auditoria.accion == "CREAR_USUARIO")
    ).all()

    assert len(registros) == 1
    assert registros[0].usuario_id == admin_user.id
    assert registros[0].entidad == "usuarios"
    assert registros[0].entidad_id == creado["id"]
    assert registros[0].detalle["username"] == "nuevo"


def test_auditoria_redacta_password(
    client: TestClient,
    db_session: Session,
    admin_headers: dict[str, str],
) -> None:
    client.put(
        "/api/usuarios/1",
        json={"nombre": "Cambiada"},
        headers=admin_headers,
    )
    auditoria_service_crear_con_secreto(db_session)

    registros = db_session.scalars(
        select(Auditoria).where(Auditoria.accion == "PRUEBA_SECRETOS")
    ).all()

    detalle = registros[0].detalle
    assert detalle["password"] == "[REDACTADO]"
    assert detalle["refreshToken"] == "[REDACTADO]"
    assert "clave-en-plano" not in str(detalle)
    assert "token-secreto" not in str(detalle)


def auditoria_service_crear_con_secreto(db_session: Session) -> None:
    from app.services import auditoria_service

    auditoria_service.registrar_auditoria(
        db_session,
        usuario_id=None,
        accion="PRUEBA_SECRETOS",
        entidad="usuarios",
        detalle={
            "password": "clave-en-plano",
            "refreshToken": "token-secreto",
            "nombre": " visible",
        },
    )


def test_auditoria_se_consulta_en_descendente_y_con_filtros(
    client: TestClient,
    db_session: Session,
    admin_headers: dict[str, str],
) -> None:
    client.post("/api/usuarios", json=payload_usuario(), headers=admin_headers)
    client.post(
        "/api/usuarios",
        json=payload_usuario(username="otro", email="otro@e.com"),
        headers=admin_headers,
    )

    todos = client.get(
        "/api/auditoria",
        params={"pagina": 1, "tamano": 10},
        headers=admin_headers,
    )
    filtrado = client.get(
        "/api/auditoria",
        params={"accion": "CREAR_USUARIO", "pagina": 1, "tamano": 10},
        headers=admin_headers,
    )

    assert todos.status_code == 200
    assert set(todos.json()) == {"items", "total", "pagina", "tamano"}
    assert todos.json()["pagina"] == 1
    assert todos.json()["tamano"] == 10
    assert todos.json()["total"] >= 2
    assert [registro["id"] for registro in todos.json()["items"]] == sorted(
        [registro["id"] for registro in todos.json()["items"]],
        reverse=True,
    )
    assert len(filtrado.json()["items"]) == 2


def test_auditoria_requiere_admin(
    client: TestClient,
    recepcion_headers: dict[str, str],
) -> None:
    assert client.get("/api/auditoria", headers=recepcion_headers).status_code == 403
    assert client.get("/api/auditoria").status_code == 401


@pytest.mark.parametrize(
    "catalogos_esperados",
    [
        "roles",
        "tipos_habitacion",
        "estados_habitacion",
        "estados_reserva",
        "metodos_pago",
        "tipos_pago",
        "tipos_documento",
    ],
)
def test_catalogos_expone_los_valores_permitidos(
    client: TestClient,
    admin_headers: dict[str, str],
    catalogos_esperados: str,
) -> None:
    respuesta = client.get("/api/catalogos", headers=admin_headers)

    assert respuesta.status_code == 200
    nombres = {catalogo["nombre"] for catalogo in respuesta.json()}
    assert catalogos_esperados in nombres


def test_catalogo_individual_por_nombre(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    respuesta = client.get("/api/catalogos/tipos_habitacion", headers=admin_headers)

    assert respuesta.status_code == 200
    assert respuesta.json()["valores"] == [
        "SIMPLE",
        "DOBLE",
        "SUITE",
        "PRESIDENCIAL",
    ]


def test_catalogo_inexistente_devuelve_404(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    respuesta = client.get("/api/catalogos/no_existe", headers=admin_headers)

    assert respuesta.status_code == 404


def test_catalogos_requieren_autenticacion(client: TestClient) -> None:
    assert client.get("/api/catalogos").status_code == 401


def test_schema_usuario_crear_rechaza_username_con_espacios() -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        UsuarioCrear(
            username="con espacio",
            email="a@example.com",
            nombre="X",
            password="clave-fuerte-1",
        )
