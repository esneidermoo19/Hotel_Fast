from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models import Auditoria, Usuario
from tests.factories import crear_auditoria, crear_usuario

BOGOTA = ZoneInfo("America/Bogota")


def crear_auditoria_en_utc(
    db_session: Session,
    *,
    usuario_id: int,
    creada_en: datetime,
    accion: str,
    entidad: str = "usuarios",
    entidad_id: int = 10,
) -> Auditoria:
    registro = Auditoria(
        usuario_id=usuario_id,
        accion=accion,
        entidad=entidad,
        entidad_id=entidad_id,
        created_at=creada_en,
    )
    db_session.add(registro)
    db_session.commit()
    db_session.refresh(registro)
    return registro


def utc_bogota(dia: date, hora: time) -> datetime:
    return datetime.combine(dia, hora, tzinfo=BOGOTA).astimezone(UTC)


def test_auditoria_paginada_filtra_y_ordena_deterministicamente(
    client: TestClient,
    db_session: Session,
    admin_user: Usuario,
    admin_headers: dict[str, str],
) -> None:
    filas = [
        crear_auditoria(
            db_session,
            usuario=admin_user,
            accion="CREAR_USUARIO",
            entidad="usuarios",
            entidad_id=10,
        ),
        crear_auditoria(
            db_session,
            usuario=admin_user,
            accion="CREAR_USUARIO",
            entidad="usuarios",
            entidad_id=10,
        ),
        crear_auditoria(
            db_session,
            usuario=admin_user,
            accion="ACTUALIZAR_USUARIO",
            entidad="usuarios",
            entidad_id=11,
        ),
        crear_auditoria(
            db_session,
            usuario=admin_user,
            accion="LOGIN",
            entidad="sesiones",
            entidad_id=12,
        ),
    ]

    primera = client.get(
        "/api/auditoria",
        params={"pagina": 1, "tamano": 2},
        headers=admin_headers,
    )
    segunda = client.get(
        "/api/auditoria",
        params={"pagina": 2, "tamano": 2},
        headers=admin_headers,
    )

    assert primera.status_code == segunda.status_code == 200
    for numero, response in ((1, primera), (2, segunda)):
        resultado = response.json()
        assert set(resultado) == {"items", "total", "pagina", "tamano"}
        assert resultado["total"] == len(filas)
        assert resultado["pagina"] == numero
        assert resultado["tamano"] == 2
    ids_primera = [registro["id"] for registro in primera.json()["items"]]
    ids_segunda = [registro["id"] for registro in segunda.json()["items"]]
    ids_paginados = ids_primera + ids_segunda
    assert ids_paginados == sorted(ids_paginados, reverse=True)
    assert len(ids_paginados) == len(set(ids_paginados)) == len(filas)
    assert set(ids_paginados) == {fila.id for fila in filas}

    por_entidad = client.get(
        "/api/auditoria",
        params={"entidad": "usuarios"},
        headers=admin_headers,
    )
    por_entidad_id = client.get(
        "/api/auditoria",
        params={"entidadId": 10},
        headers=admin_headers,
    )
    por_accion = client.get(
        "/api/auditoria",
        params={"accion": "CREAR_USUARIO"},
        headers=admin_headers,
    )
    assert (
        por_entidad.status_code
        == por_entidad_id.status_code
        == por_accion.status_code
        == 200
    )
    assert por_entidad.json()["total"] == 3
    assert por_entidad_id.json()["total"] == 2
    assert por_accion.json()["total"] == 2


@pytest.mark.parametrize("tamano", [0, 101])
def test_auditoria_rechaza_tamano_fuera_de_rango(
    client: TestClient,
    admin_headers: dict[str, str],
    tamano: int,
) -> None:
    response = client.get(
        "/api/auditoria",
        params={"pagina": 1, "tamano": tamano},
        headers=admin_headers,
    )

    assert response.status_code == 422
    assert set(response.json()) == {"detail", "code", "errors"}
    assert response.json()["code"] == "VALIDACION"
    assert response.json()["errors"]


def test_auditoria_filtros_usuario_y_rango_bogota(
    client: TestClient,
    db_session: Session,
    admin_user: Usuario,
    admin_headers: dict[str, str],
) -> None:
    otro_usuario = crear_usuario(
        db_session,
        username="auditoria-otro",
        email="auditoria-otro@example.com",
    )
    dia = date(2026, 10, 4)
    anterior = crear_auditoria_en_utc(
        db_session,
        usuario_id=admin_user.id,
        creada_en=utc_bogota(dia - timedelta(days=1), time(23, 59)),
        accion="LOGIN",
    )
    inicio = crear_auditoria_en_utc(
        db_session,
        usuario_id=admin_user.id,
        creada_en=utc_bogota(dia, time(0, 1)),
        accion="CONSULTA",
        entidad_id=7,
    )
    fin = crear_auditoria_en_utc(
        db_session,
        usuario_id=admin_user.id,
        creada_en=utc_bogota(dia, time(23, 59)),
        accion="LOGIN",
        entidad_id=8,
    )
    de_otro_usuario = crear_auditoria_en_utc(
        db_session,
        usuario_id=otro_usuario.id,
        creada_en=utc_bogota(dia, time(12, 0)),
        accion="LOGIN",
        entidad_id=8,
    )
    posterior = crear_auditoria_en_utc(
        db_session,
        usuario_id=admin_user.id,
        creada_en=utc_bogota(dia + timedelta(days=1), time(0, 1)),
        accion="LOGIN",
        entidad_id=8,
    )

    por_usuario = client.get(
        "/api/auditoria",
        params={"usuarioId": admin_user.id},
        headers=admin_headers,
    )
    desde = client.get(
        "/api/auditoria",
        params={"desde": dia.isoformat()},
        headers=admin_headers,
    )
    hasta = client.get(
        "/api/auditoria",
        params={"hasta": dia.isoformat()},
        headers=admin_headers,
    )
    rango_dia = client.get(
        "/api/auditoria",
        params={"desde": dia.isoformat(), "hasta": dia.isoformat()},
        headers=admin_headers,
    )

    assert por_usuario.status_code == desde.status_code == hasta.status_code == 200
    assert por_usuario.json()["total"] == 4
    assert desde.json()["total"] == 4
    assert hasta.json()["total"] == 4
    assert rango_dia.json()["total"] == 3
    ids_del_dia = {item["id"] for item in rango_dia.json()["items"]}
    assert ids_del_dia == {inicio.id, fin.id, de_otro_usuario.id}
    assert anterior.id not in ids_del_dia
    assert posterior.id not in ids_del_dia

    inicio_json = next(
        registro
        for registro in rango_dia.json()["items"]
        if registro["id"] == inicio.id
    )
    instante_normalizado = datetime.fromisoformat(inicio_json["createdAt"])
    assert instante_normalizado.utcoffset() == timedelta(0)

    combinados = client.get(
        "/api/auditoria",
        params={
            "usuarioId": admin_user.id,
            "desde": dia.isoformat(),
            "hasta": dia.isoformat(),
            "entidad": "usuarios",
            "entidadId": 8,
            "accion": "LOGIN",
        },
        headers=admin_headers,
    )
    assert combinados.status_code == 200
    assert combinados.json()["total"] == 1
    assert [registro["id"] for registro in combinados.json()["items"]] == [fin.id]


def test_auditoria_usuario_sin_eventos_devuelve_pagina_vacia(
    client: TestClient,
    db_session: Session,
    admin_headers: dict[str, str],
) -> None:
    usuario = crear_usuario(
        db_session,
        username="sin-eventos",
        email="sin-eventos@example.com",
    )

    response = client.get(
        "/api/auditoria",
        params={"usuarioId": usuario.id},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total"] == 0


def test_auditoria_rango_invertido_devuelve_validacion(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.get(
        "/api/auditoria",
        params={"desde": "2026-10-05", "hasta": "2026-10-04"},
        headers=admin_headers,
    )

    assert response.status_code == 422
    assert set(response.json()) == {"detail", "code", "errors"}
    assert response.json()["code"] == "VALIDACION"
    assert response.json()["errors"] == []
    assert "posterior" in response.json()["detail"]


def test_auditoria_documenta_nuevos_filtros_en_openapi() -> None:
    operacion = app.openapi()["paths"]["/api/auditoria"]["get"]
    parametros = {parametro["name"]: parametro for parametro in operacion["parameters"]}

    assert {"usuarioId", "desde", "hasta"} <= parametros.keys()
    assert all(
        parametros[nombre]["description"]
        for nombre in ("usuarioId", "desde", "hasta")
    )


def test_auditoria_requiere_admin(
    client: TestClient,
    recepcion_headers: dict[str, str],
) -> None:
    response = client.get("/api/auditoria", headers=recepcion_headers)

    assert response.status_code == 403
